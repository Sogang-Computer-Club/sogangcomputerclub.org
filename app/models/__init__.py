"""
Models package.
Re-exports tables from domain modules for backward compatibility and Alembic.
"""

from ..memos.models import memos

__all__ = ["memos"]
