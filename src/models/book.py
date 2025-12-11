from sqlalchemy import Column, Integer, String
from src.core.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)
    author = Column(String, nullable=False)

    year = Column(Integer, nullable=False)
    isbn = Column(String, unique=True, nullable=False, index=True)

    copies_available = Column(Integer, default=0, nullable=False)
