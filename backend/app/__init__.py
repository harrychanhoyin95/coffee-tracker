from sanic import Sanic, Request
from sanic.log import logger
from sanic.response import text
from sanic.exceptions import ServerError
from types import SimpleNamespace

from app.database import init_db, close_db
from app.api import v1_blueprint

async def create_app():
  # Initialize Sanic app with context
  app = Sanic("CoffeeTrackerAPI")
  app.ctx = SimpleNamespace()

  @app.before_server_start
  async def before_start(app, loop):
    """Initialize database before server starts"""
    try:
      await init_db(app)
    except Exception as e:
      logger.error(f"[app.py] Failed to initialize database: {e}")
      raise ServerError("[app.py] Database initialization failed")
    
  @app.after_server_stop
  async def after_stop(app, loop):
    """Cleanup database connections after server stops"""
    try:
      await close_db(app)
    except Exception as e:
      logger.error(f"[app.py] Failed to close database connections: {e}")
      raise ServerError("[app.py] Database closing failed")

  @app.get("/")
  async def root(request: Request):
    return text("Hello World!")

  # Register blueprints
  app.blueprint(v1_blueprint, url_prefix="/api/v1")

  return app
