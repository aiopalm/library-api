from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.reader import Reader
from src.models.user import User
from src.schemas.reader import ReaderCreate, ReaderUpdate, ReaderResponse, ReaderList

router = APIRouter()


@router.post(
    "/",
    response_model=ReaderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reader"
)
async def create_reader(
        reader_data: ReaderCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Reader).where(Reader.email == reader_data.email)
    )
    existing_reader = result.scalar_one_or_none()

    if existing_reader:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reader with email {reader_data.email} already exists"
        )

    new_reader = Reader(
        name=reader_data.name,
        email=reader_data.email
    )

    db.add(new_reader)
    await db.commit()
    await db.refresh(new_reader)

    return new_reader


@router.get(
    "/",
    response_model=ReaderList,
    summary="Get all readers"
)
async def get_readers(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    count_result = await db.execute(select(func.count(Reader.id)))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Reader)
        .order_by(Reader.id)
    )
    readers = result.scalars().all()

    return ReaderList(readers=readers, total=total)


@router.get(
    "/{reader_id}",
    response_model=ReaderResponse,
    summary="Get reader by ID"
)
async def get_reader(
        reader_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Reader).where(Reader.id == reader_id)
    )
    reader = result.scalar_one_or_none()

    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader {reader_id} not found"
        )

    return reader


@router.put(
    "/{reader_id}",
    response_model=ReaderResponse,
    summary="Update reader"
)
async def update_reader(
        reader_id: int,
        reader_data: ReaderUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Get existing reader
    result = await db.execute(
        select(Reader).where(Reader.id == reader_id)
    )
    reader = result.scalar_one_or_none()

    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader {reader_id} not found"
        )

    if reader_data.email and reader_data.email != reader.email:
        email_check = await db.execute(
            select(Reader).where(Reader.email == reader_data.email)
        )
        if email_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reader with email {reader_data.email} already exists"
            )

    update_data = reader_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reader, field, value)

    await db.commit()
    await db.refresh(reader)

    return reader


@router.delete(
    "/{reader_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete reader"
)
async def delete_reader(
        reader_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Reader).where(Reader.id == reader_id)
    )
    reader = result.scalar_one_or_none()

    if not reader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reader {reader_id} not found"
        )

    await db.delete(reader)
    await db.commit()

    return None
