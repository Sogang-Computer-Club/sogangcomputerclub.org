"""Routers package."""
from .health import router as health_router
from .memos import router as memos_router
from .auth import router as auth_router

__all__ = ["health_router", "memos_router", "auth_router"]
