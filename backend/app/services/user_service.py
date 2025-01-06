from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import User

from app.utils.exceptions import NotFoundError

class UserService:
  def __init__(self, session: AsyncSession):
    self._session = session
    
  @staticmethod
  def _serialize_user(user: User) -> Dict:
    """
    Convert a User model instance to a dictionary
    
    Args:
        user: User model instance
        
    Returns:
        Dict containing the user's information
    """
    return {
      "id": user.id,
      "email": user.email,
      "created_at": str(user.created_at),
      "updated_at": str(user.updated_at)
    }
    
  async def get_users(self) -> List[Dict]:
    """
    Retrieve all users from the database
    """
    async with self._session.begin():
      stmt = select(User)
      result = await self._session.execute(stmt)
      users = result.scalars().all()

      return [self._serialize_user(user) for user in users]

  async def get_user_by_id(self, user_id: int) -> Optional[Dict]:
    """
    Retrieve a user by their ID
    
    Args:
        user_id: ID of the user to retrieve
        
    Returns:
        Dict containing the user's information
    """
    async with self._session.begin():
      stmt = select(User).where(User.id == user_id)
      result = await self._session.execute(stmt)
      user = result.scalar_one_or_none()

      if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

      return self._serialize_user(user) if user else None

  async def create_user(self, email: str) -> Dict:
    """
    Create a new user
    
    Args:
        email: Email address of the user to create
        
    Returns:
        Dict containing the user's information
    """
    async with self._session.begin():
      user = User(email=email)
      self._session.add(user)
      await self._session.flush()
      await self._session.refresh(user)

      return self._serialize_user(user)
