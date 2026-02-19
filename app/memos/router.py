"""
Memo CRUD API endpoints.
Thin router that delegates to MemoService.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request, Query
from typing import List
import logging

from .schemas import MemoCreate, MemoUpdate, MemoInDB
from .service import MemoService, MemoNotFoundError, MemoForbiddenError
from .dependencies import get_memo_service
from ..users.dependencies import require_auth
from ..common.rate_limit import limiter, RATE_LIMIT_WRITE, RATE_LIMIT_SEARCH, RATE_LIMIT_DEFAULT

router = APIRouter(prefix="/memos", tags=["Memos"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=MemoInDB, status_code=status.HTTP_201_CREATED)
@limiter.limit(RATE_LIMIT_WRITE)
async def create_memo(
    request: Request,
    memo: MemoCreate,
    service: MemoService = Depends(get_memo_service),
    current_user: dict = Depends(require_auth)
):
    """Create a new memo. Requires authentication."""
    try:
        user_email = current_user.get("sub", memo.author)
        return await service.create_memo(memo, user_email)
    except Exception as e:
        logger.error(f"메모 생성 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메모 생성에 실패했습니다."
        )


@router.get("/", response_model=List[MemoInDB])
@limiter.limit(RATE_LIMIT_DEFAULT)
async def read_memos(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    service: MemoService = Depends(get_memo_service)
):
    """Get all memos."""
    try:
        return await service.get_memos(skip, limit)
    except Exception as e:
        logger.error(f"메모 목록 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메모를 불러오는 데 실패했습니다."
        )


@router.get("/search/", response_model=List[MemoInDB])
@limiter.limit(RATE_LIMIT_SEARCH)
async def search_memos(
    request: Request,
    q: str = Query(..., min_length=1, max_length=100, description="검색어"),
    skip: int = Query(default=0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(default=100, ge=1, le=500, description="최대 반환 항목 수"),
    service: MemoService = Depends(get_memo_service)
):
    """Search memos by keyword with pagination."""
    try:
        return await service.search_memos(q, skip, limit)
    except Exception as e:
        logger.error(f"메모 검색 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메모 검색 중 오류가 발생했습니다."
        )


@router.get("/{memo_id}", response_model=MemoInDB)
@limiter.limit(RATE_LIMIT_DEFAULT)
async def read_memo(
    request: Request,
    memo_id: int,
    service: MemoService = Depends(get_memo_service)
):
    """Get a specific memo by ID."""
    try:
        return await service.get_memo(memo_id)
    except MemoNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메모 조회 중 오류가 발생했습니다."
        )


@router.put("/{memo_id}", response_model=MemoInDB)
@limiter.limit(RATE_LIMIT_WRITE)
async def update_memo(
    request: Request,
    memo_id: int,
    memo: MemoUpdate,
    service: MemoService = Depends(get_memo_service),
    current_user: dict = Depends(require_auth)
):
    """Update a memo. Requires authentication and ownership."""
    try:
        return await service.update_memo(memo_id, memo, current_user)
    except MemoNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MemoForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 수정 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메모 수정 중 오류가 발생했습니다."
        )


@router.delete("/{memo_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit(RATE_LIMIT_WRITE)
async def delete_memo(
    request: Request,
    memo_id: int,
    service: MemoService = Depends(get_memo_service),
    current_user: dict = Depends(require_auth)
):
    """Delete a memo. Requires authentication and ownership."""
    try:
        await service.delete_memo(memo_id, current_user)
        return None
    except MemoNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except MemoForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"메모(ID:{memo_id}) 삭제 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메모 삭제 중 오류가 발생했습니다."
        )
