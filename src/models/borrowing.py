from datetime import datetime

from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql import func

from src.core.database import Base


class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    reader_id: Mapped[int] = mapped_column(Integer, ForeignKey("readers.id", ondelete="CASCADE"), nullable=False)

    borrow_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    return_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
