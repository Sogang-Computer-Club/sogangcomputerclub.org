"""
Memo CRUD API endpoints.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import sqlalchemy
import logging

from ..schemas.memo import MemoCreate, MemoUpdate, MemoInDB
from ..models.memo import memos
from ..dependencies import get_db
from ..metrics import MEMO_COUNT

router = APIRouter(prefix="/memos", tags=["Memos"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=MemoInDB, status_code=status.HTTP_201_CREATED)
async def create_memo(memo: MemoCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """Create a new memo."""
    try:
        query = memos.insert().values(
            title=memo.title,
            content=memo.content,
            tags=memo.tags or [],
            priority=memo.priority,
            category=memo.category,
            is_archived=memo.is_archived,
            is_favorite=memo.is_favorite,
            author=memo.author
        ).returning(memos.c.id)
        result = await db.execute(query)
        created_id = result.scalar_one()
        await db.commit()
        created_memo_query = memos.select().where(memos.c.id == created_id)
        created_memo = await db.execute(created_memo_query)
        memo_data = created_memo.mappings().one()

        # Publish to Kafka
        if request.app.state.kafka:
            await request.app.state.kafka.publish(
                "memo-created",
                {"id": created_id, "title": memo.title, "action": "created"}
            )

        MEMO_COUNT.inc()
        return memo_data
    except Exception as e:
        await db.rollback()
        logger.error(f"메모 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 생성에 실패했습니다.")


@router.get("/", response_model=List[MemoInDB])
async def read_memos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Get all memos."""
    try:
        query = memos.select().order_by(memos.c.id.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.mappings().all()
    except Exception as e:
        logger.error(f"메모 목록 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모를 불러오는 데 실패했습니다.")


@router.get("/search/", response_model=List[MemoInDB])
async def search_memos(q: str = Query(..., min_length=1, description="검색어"), db: AsyncSession = Depends(get_db)):
    """Search memos by keyword."""
    try:
        search_query = f"%{q}%"
        query = memos.select().where(
            sqlalchemy.or_(
                memos.c.title.like(search_query),
                memos.c.content.like(search_query)
            )
        ).order_by(memos.c.id.desc())

        result = await db.execute(query)
        return result.mappings().all()
    except Exception as e:
        logger.error(f"메모 검색 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 검색 중 오류가 발생했습니다.")


@router.get("/{memo_id}", response_model=MemoInDB)
async def read_memo(memo_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific memo by ID."""
    try:
        query = memos.select().where(memos.c.id == memo_id)
        result = await db.execute(query)
        memo = result.mappings().first()
        if memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")
        return memo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 조회 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 조회 중 오류가 발생했습니다.")


@router.put("/{memo_id}", response_model=MemoInDB)
async def update_memo(memo_id: int, memo: MemoUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    """Update a memo."""
    try:
        existing_memo_query = memos.select().where(memos.c.id == memo_id)
        existing_memo = (await db.execute(existing_memo_query)).mappings().first()
        if existing_memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        update_data = memo.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 내용이 없습니다.")

        query = memos.update().where(memos.c.id == memo_id).values(**update_data)
        await db.execute(query)
        await db.commit()

        updated_memo_query = memos.select().where(memos.c.id == memo_id)
        updated_memo = (await db.execute(updated_memo_query)).mappings().one()

        # Publish to Kafka
        if request.app.state.kafka:
            await request.app.state.kafka.publish(
                "memo-updated",
                {"id": memo_id, "action": "updated"}
            )

        return updated_memo
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"메모(ID:{memo_id}) 수정 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 수정 중 오류가 발생했습니다.")


@router.delete("/{memo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memo(memo_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Delete a memo."""
    try:
        existing_memo_query = memos.select().where(memos.c.id == memo_id)
        existing_memo = (await db.execute(existing_memo_query)).mappings().first()
        if existing_memo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID {memo_id}에 해당하는 메모를 찾을 수 없습니다.")

        delete_query = memos.delete().where(memos.c.id == memo_id)
        await db.execute(delete_query)
        await db.commit()

        # Publish to Kafka
        if request.app.state.kafka:
            await request.app.state.kafka.publish(
                "memo-deleted",
                {"id": memo_id, "action": "deleted"}
            )

        MEMO_COUNT.dec()
        return None
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"메모(ID:{memo_id}) 삭제 중 오류 발생: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="메모 삭제 중 오류가 발생했습니다.")
