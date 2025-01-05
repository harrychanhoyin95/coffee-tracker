from sqlalchemy import INTEGER, Column
from sqlalchemy.orm import declarative_base
import time

Base = declarative_base()

class BaseModel(Base):
  __abstract__ = True
  id = Column(INTEGER, primary_key=True)
  created_at = Column(INTEGER, default=lambda: int(time.time()))
  updated_at = Column(INTEGER, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))
