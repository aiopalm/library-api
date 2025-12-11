from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from src.core.database import Base

class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    reader_id = Column(Integer, ForeignKey("readers.id", ondelete="CASCADE"), nullable=False)

    borrow_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
