"""
데이터베이스 연결 및 세션 관리.
"""
import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import get_settings

metadata = sqlalchemy.MetaData()

settings = get_settings()

# 비동기 데이터베이스 엔진 (커넥션 풀링 설정)
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=10,        # 풀에 유지할 기본 커넥션 수
    max_overflow=20,     # 풀이 가득 찼을 때 추가로 생성할 수 있는 커넥션 수
    pool_timeout=30,     # 커넥션 대기 최대 시간 (초)
    pool_recycle=3600,   # 커넥션 재활용 주기 (초) - DB의 wait_timeout 이내로 설정
    pool_pre_ping=True   # 사용 전 커넥션 유효성 검사 (끊어진 커넥션 자동 복구)
)

# 세션 팩토리 - 각 요청마다 새 세션 생성
# autocommit=False: 명시적 commit 필요, autoflush=False: 수동 flush로 성능 최적화
async_session_factory = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)
