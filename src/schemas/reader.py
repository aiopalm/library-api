from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ReaderBase(BaseModel):
    """Base schema for Reader with common fields"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr = Field(...)


class ReaderCreate(ReaderBase):
    pass


class ReaderUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None


class ReaderResponse(ReaderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ReaderList(BaseModel):
    readers: list[ReaderResponse]
    total: int
