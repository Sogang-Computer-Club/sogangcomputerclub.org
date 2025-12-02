"""
데이터베이스 테이블 초기화 스크립트
CI 환경에서 integration test 실행 전에 사용
"""
import asyncio
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine

# 테이블 정의 (app/main.py에서 가져옴)
metadata = sqlalchemy.MetaData()

memos = sqlalchemy.Table(
    "memos",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("title", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("content", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("tags", sqlalchemy.JSON, nullable=True, default=[]),
    sqlalchemy.Column("priority", sqlalchemy.Integer, nullable=False, default=2, server_default="2"),
    sqlalchemy.Column("category", sqlalchemy.String(50), nullable=True),
    sqlalchemy.Column("is_archived", sqlalchemy.Boolean, nullable=False, default=False, server_default="0"),
    sqlalchemy.Column("is_favorite", sqlalchemy.Boolean, nullable=False, default=False, server_default="0"),
    sqlalchemy.Column("author", sqlalchemy.String(100), nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now()),
)


async def init_db():
    """데이터베이스 테이블 생성"""
    # CI 환경의 MariaDB 설정
    import os
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://memo_user:phoenix@localhost:5432/memo_app"
    )

    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # 테이블 생성
        await conn.run_sync(metadata.create_all)

    await engine.dispose()
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
