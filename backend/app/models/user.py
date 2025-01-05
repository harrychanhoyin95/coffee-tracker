from sqlalchemy import Column, String, func
from sqlalchemy.ext.hybrid import hybrid_property

from app.models.base import BaseModel

class User(BaseModel):
  __tablename__ = 'users'
  _email = Column('email', String, unique=True)

  @hybrid_property
  def email(self):
    """Getting the email always returns lowercase"""
    return self._email.lower() if self._email else None
        
  @email.setter
  def email(self, value):
    """Setting the email always stores lowercase"""
    self._email = value.lower() if value else None
    
  @email.expression
  def email(cls):
    """Ensures database queries also use lowercase"""
    return func.lower(cls._email)
