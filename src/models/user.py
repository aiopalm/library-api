from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
