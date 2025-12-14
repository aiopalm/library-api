from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.book import Book
from src.models.reader import Reader
from src.models.borrowing import BorrowedBook
from src.models.user import User
from src.schemas.borrowing import (
    BorrowingCreate,
    BorrowingReturn,
    BorrowingResponse,
    BorrowingDetailResponse,
    BorrowingList,
    ActiveBorrowingResponse
)

router = APIRouter()


@router.post(
    "/borrow",
    response_model=BorrowingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Borrow a book"
)
async def borrow_book(
        borrow_data: BorrowingCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    book_result = await db.execute(
        select(Book).where(Book.id == borrow_data.book_id)
    )
    book = book_result.scalar_one_or_none()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with id {borrow_data.book_id} not found"
        )

    reader_result = await db.execute(
        select(Reader).where(Reader.id == borrow_data.reader_id)
    )
    reader = reader_result.scalar_one_or_none()

    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader with id {borrow_data.reader_id} not found"
        )

    if book.copies_available <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Book '{book.title}' has no available copies"
        )

    active_borrowings_result = await db.execute(
        select(func.count(BorrowedBook.id))
        .where(
            and_(
                BorrowedBook.reader_id == borrow_data.reader_id,
                BorrowedBook.return_date.is_(None)
            )
        )
    )
    active_count = active_borrowings_result.scalar_one()

    if active_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reader '{reader.name}' already has {active_count} active borrowings. Maximum is 3."
        )

    existing_borrow_result = await db.execute(
        select(BorrowedBook)
        .where(
            and_(
                BorrowedBook.book_id == borrow_data.book_id,
                BorrowedBook.reader_id == borrow_data.reader_id,
                BorrowedBook.return_date.is_(None)
            )
        )
    )
    existing_borrow = existing_borrow_result.scalar_one_or_none()

    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reader '{reader.name}' already has this book and hasn't returned it yet"
        )

    new_borrowing = BorrowedBook(
        book_id=borrow_data.book_id,
        reader_id=borrow_data.reader_id
    )

    book.copies_available -= 1

    db.add(new_borrowing)
    await db.commit()
    await db.refresh(new_borrowing)

    return new_borrowing


@router.post(
    "/return",
    response_model=BorrowingResponse,
    summary="Return a book"
)
async def return_book(
        return_data: BorrowingReturn,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(BorrowedBook)
        .where(
            and_(
                BorrowedBook.book_id == return_data.book_id,
                BorrowedBook.reader_id == return_data.reader_id,
                BorrowedBook.return_date.is_(None)
            )
        )
    )
    borrowing = result.scalar_one_or_none()

    if not borrowing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This book was not borrowed by this reader or was already returned"
        )

    book_result = await db.execute(
        select(Book).where(Book.id == return_data.book_id)
    )
    book = book_result.scalar_one()

    borrowing.return_date = datetime.now(timezone.utc)
    book.copies_available += 1

    await db.commit()
    await db.refresh(borrowing)

    return borrowing


@router.get(
    "/",
    response_model=BorrowingList,
    summary="Get all borrowing records"
)
async def get_all_borrowings(
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
        active_only: bool = Query(False, description="Show only active (not returned) borrowings"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    query = select(BorrowedBook).options(
        selectinload(BorrowedBook.book),
        selectinload(BorrowedBook.reader)
    )

    if active_only:
        query = query.where(BorrowedBook.return_date.is_(None))

    count_query = select(func.count(BorrowedBook.id))
    if active_only:
        count_query = count_query.where(BorrowedBook.return_date.is_(None))

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    query = query.offset(skip).limit(limit).order_by(BorrowedBook.borrow_date.desc())
    result = await db.execute(query)
    borrowings = result.scalars().all()

    detail_borrowings = []
    for b in borrowings:
        detail_borrowings.append(
            BorrowingDetailResponse(
                id=b.id,
                book=b.book,
                reader=b.reader,
                borrow_date=b.borrow_date,
                return_date=b.return_date
            )
        )

    return BorrowingList(borrowings=detail_borrowings, total=total)


@router.get(
    "/reader/{reader_id}",
    response_model=list[ActiveBorrowingResponse],
    summary="Get reader's active borrowings"
)
async def get_reader_active_borrowings(
        reader_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    reader_result = await db.execute(
        select(Reader).where(Reader.id == reader_id)
    )
    reader = reader_result.scalar_one_or_none()

    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader with id {reader_id} not found"
        )

    result = await db.execute(
        select(BorrowedBook)
        .options(selectinload(BorrowedBook.book))
        .where(
            and_(
                BorrowedBook.reader_id == reader_id,
                BorrowedBook.return_date.is_(None)
            )
        )
        .order_by(BorrowedBook.borrow_date.desc())
    )
    borrowings = result.scalars().all()

    active_borrowings = [
        ActiveBorrowingResponse(
            book=b.book,
            borrow_date=b.borrow_date
        )
        for b in borrowings
    ]

    return active_borrowings


@router.get(
    "/{borrowing_id}",
    response_model=BorrowingDetailResponse,
    summary="Get borrowing by ID"
)
async def get_borrowing(
        borrowing_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(BorrowedBook)
        .options(
            selectinload(BorrowedBook.book),
            selectinload(BorrowedBook.reader)
        )
        .where(BorrowedBook.id == borrowing_id)
    )
    borrowing = result.scalar_one_or_none()

    if not borrowing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrowing record with id {borrowing_id} not found"
        )

    return BorrowingDetailResponse(
        id=borrowing.id,
        book=borrowing.book,
        reader=borrowing.reader,
        borrow_date=borrowing.borrow_date,
        return_date=borrowing.return_date
    )
