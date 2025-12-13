from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.book import Book
from src.models.user import User
from src.schemas.book import BookCreate, BookUpdate, BookResponse, BookList

router = APIRouter()


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create book"
)
async def create_book(
        book_data: BookCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Book).where(Book.isbn == book_data.isbn)
    )
    existing_book = result.scalar_one_or_none()

    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book with ISBN {book_data.isbn} already exists"
        )

    new_book = Book(
        title=book_data.title,
        author=book_data.author,
        year=book_data.year,
        isbn=book_data.isbn,
        copies_available=book_data.copies_available,
        description=book_data.description or ""
    )

    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)

    return new_book


@router.get(
    "/",
    response_model=BookList,
    summary="Get all books"
)
async def get_books(
        db: AsyncSession = Depends(get_db)
):
    count_result = await db.execute(select(func.count(Book.id)))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Book)
        .order_by(Book.id)
    )
    books = result.scalars().all()

    return BookList(books=books, total=total)


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    summary="Get book"
)
async def get_book(
        book_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Book).where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )

    return book


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    summary="Update book"
)
async def update_book(
        book_id: int,
        book_data: BookUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Book).where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {book_id} not found"
        )

    if book_data.isbn and book_data.isbn != book.isbn:
        isbn_check = await db.execute(
            select(Book).where(Book.isbn == book_data.isbn)
        )
        if isbn_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with ISBN {book_data.isbn} already exists"
            )

    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    await db.commit()
    await db.refresh(book)

    return book


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete book"
)
async def delete_book(
        book_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Book).where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {book_id} not found"
        )

    await db.delete(book)
    await db.commit()

    return None
