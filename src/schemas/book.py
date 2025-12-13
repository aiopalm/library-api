from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    year: int = Field(..., ge=1000, le=9999)
    isbn: str = Field(..., min_length=10, max_length=17)
    description: str | None = Field(None)


class BookCreate(BookBase):
    copies_available: int = Field(..., ge=0)


class BookUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    author: str | None = Field(None, min_length=1, max_length=255)
    year: int | None = Field(None, ge=1000, le=9999)
    isbn: str | None = Field(None, min_length=10, max_length=17)
    description: str | None = None
    copies_available: int | None = Field(None, ge=0)


class BookResponse(BookBase):
    id: int
    copies_available: int

    model_config = ConfigDict(from_attributes=True)


class BookList(BaseModel):
    books: list[BookResponse]
    total: int
