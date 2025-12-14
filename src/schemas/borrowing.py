from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from src.schemas.book import BookResponse
from src.schemas.reader import ReaderResponse


class BorrowingBase(BaseModel):
    book_id: int = Field(..., gt=0)
    reader_id: int = Field(..., gt=0)


class BorrowingCreate(BorrowingBase):
    pass


class BorrowingReturn(BaseModel):
    book_id: int = Field(..., gt=0)
    reader_id: int = Field(..., gt=0)


class BorrowingResponse(BorrowingBase):
    id: int
    borrow_date: datetime
    return_date: datetime | None

    model_config = ConfigDict(from_attributes=True)


class BorrowingDetailResponse(BaseModel):
    id: int
    book: BookResponse
    reader: ReaderResponse
    borrow_date: datetime
    return_date: datetime | None

    model_config = ConfigDict(from_attributes=True)


class BorrowingList(BaseModel):
    borrowings: list[BorrowingDetailResponse]
    total: int


class ActiveBorrowingResponse(BaseModel):
    book: BookResponse
    borrow_date: datetime

    model_config = ConfigDict(from_attributes=True)
