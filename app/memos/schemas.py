"""
Memo Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class MemoBase(BaseModel):
    """Base memo schema with common fields."""

    title: str = Field(..., min_length=1, max_length=100, description="메모 제목")
    content: str = Field(..., min_length=1, description="메모 내용")
    tags: list[str] | None = Field(default=[], description="태그 목록")
    priority: int = Field(
        default=2, ge=1, le=4, description="우선순위 (1:낮음, 2:보통, 3:높음, 4:긴급)"
    )
    category: str | None = Field(None, max_length=50, description="카테고리")
    is_archived: bool = Field(default=False, description="아카이브 여부")
    is_favorite: bool = Field(default=False, description="즐겨찾기 여부")
    author: str | None = Field(None, max_length=100, description="작성자")


class MemoCreate(MemoBase):
    """Schema for creating a new memo."""

    pass


class MemoUpdate(BaseModel):
    """Schema for updating an existing memo. All fields optional."""

    title: str | None = Field(None, min_length=1, max_length=100)
    content: str | None = Field(None, min_length=1)
    tags: list[str] | None = None
    priority: int | None = Field(None, ge=1, le=4)
    category: str | None = Field(None, max_length=50)
    is_archived: bool | None = None
    is_favorite: bool | None = None
    author: str | None = Field(None, max_length=100)


class MemoInDB(MemoBase):
    """Schema for memo as stored in database."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
