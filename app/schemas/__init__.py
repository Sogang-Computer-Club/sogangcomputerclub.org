"""
Schemas package.
Re-exports schemas from domain modules for backward compatibility.
"""

from ..memos.schemas import MemoBase, MemoCreate, MemoUpdate, MemoInDB
from ..users.schemas import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserInDB,
    Token,
    TokenData,
)

__all__ = [
    "MemoBase",
    "MemoCreate",
    "MemoUpdate",
    "MemoInDB",
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserInDB",
    "Token",
    "TokenData",
]
