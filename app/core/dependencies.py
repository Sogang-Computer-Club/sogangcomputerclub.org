"""
FastAPI 의존성 주입 함수.
"""
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    요청별 데이터베이스 세션 제공.

    FastAPI의 Depends()를 통해 각 요청에 독립적인 세션 주입.
    - 예외 발생 시 자동 롤백하여 데이터 무결성 유지
    - 요청 종료 시 세션 자동 정리
    """
    session_factory = request.app.state.db_session_factory
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
