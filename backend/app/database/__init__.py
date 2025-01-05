from sanic import Request
from sanic.log import logger
from typing import TypeVar, Optional, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from contextlib import AbstractAsyncContextManager
from types import SimpleNamespace
from dataclasses import dataclass
from contextvars import ContextVar
import os

from app.models.base import Base

# Type variables for better type hints
T = TypeVar('T')
AppType = TypeVar('AppType', bound=SimpleNamespace)

# Context variable for session management
_base_model_session_ctx = ContextVar("session")

@dataclass
class DatabaseConfig:
  """Database configuration with environment variable support and validation"""
  url = os.getenv("DATABASE_URL", 'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres')
  echo: bool = bool(os.getenv("DATABASE_ECHO", "True"))
  pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
  max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
  
  def __post_init__(self) -> None:
    """Validate configuration after initialization"""
    if not self.url:
        raise ValueError("[database.py] Database URL cannot be empty")
    if self.pool_size < 1:
        raise ValueError("[database.py] Pool size must be at least 1")
    if self.max_overflow < 0:
        raise ValueError("[database.py] Max overflow must be non-negative")

class Database:
  """Singleton database manager with connection pooling"""
  _instance: Optional['Database'] = None
  
  def __init__(self) -> None:
    if Database._instance is not None:
      raise RuntimeError("[database.py] Database instance already exists. Use get_instance()")
    self.engine: Optional[AsyncEngine] = None
    self._session_factory: Optional[sessionmaker] = None
    self.config = DatabaseConfig()
  
  @classmethod
  def get_instance(cls) -> 'Database':
    """Returns the singleton instance of Database"""
    if cls._instance is None:
      cls._instance = cls()
    return cls._instance
  
  async def initialize(self, app: SimpleNamespace) -> None:
    """Initializes database engine and session factory
    
    Args:
        app: Application instance to attach database context
        
    Raises:
        RuntimeError: If initialization fails
    """
    try:
      self.engine = create_async_engine(
        self.config.url,
        echo=self.config.echo,
        pool_size=self.config.pool_size,
        max_overflow=self.config.max_overflow
      )
      
      self._session_factory = sessionmaker(
        self.engine,
        class_=AsyncSession,
        expire_on_commit=False
      )
      
      app.ctx.db = self
      
      async with self.engine.begin() as conn:
        logger.info("[database.py] Initializing database...")
        await conn.run_sync(Base.metadata.create_all)
        
      logger.info("[database.py] Database initialized")
    
    except Exception as e:
      logger.error(f"[database.py] Database initialization failed: {str(e)}")
      raise RuntimeError(f"[database.py] Database initialization failed: {str(e)}") from e
  
  async def dispose(self) -> None:
    """Closes database connections"""
    if self.engine:
      try:
          await self.engine.dispose()
          logger.info("[database.py] Database connections closed")
      
      except Exception as e:
        logger.error(f"[database.py] Database disposal failed: {str(e)}")
        raise 
  
  @property
  def session(self) -> AbstractAsyncContextManager[AsyncSession]:
    """Property to access session context manager
    
    Raises:
        RuntimeError: If database is not initialized
    """
    if not self.session_manager:
      raise RuntimeError("[database.py] Database not initialized. Call initialize() first")
    return self.session_manager.get_session()

def get_session() -> AsyncSession:
    """Get the current request's database session from context
    
    Returns:
        AsyncSession: The current database session
        
    Raises:
        LookupError: If called outside of a request context
    """
    return _base_model_session_ctx.get()

# Middleware functions
async def inject_session(request: Request) -> None:
  """Middleware to inject database session into request context"""
  db = Database.get_instance()
  request.ctx.session = db._session_factory()
  request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)
  
async def close_session(request: Request, response: Any) -> None:
  """Middleware to cleanup database session after request"""
  if hasattr(request.ctx, "session_ctx_token"):
    _base_model_session_ctx.reset(request.ctx.session_ctx_token)
    await request.ctx.session.close()

# Application lifecycle functions
async def init_db(app: AppType) -> None:
    """Initialize database during application startup"""
    await Database.get_instance().initialize(app)
    
    # Register middleware
    app.middleware("request")(inject_session)
    app.middleware("response")(close_session)

async def close_db(app: AppType) -> None:
    """Cleanup database connections during application shutdown"""
    await Database.get_instance().dispose()
