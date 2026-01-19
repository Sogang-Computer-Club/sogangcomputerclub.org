"""
Memo database model (SQLAlchemy Table).
"""
import sqlalchemy
from ..database import metadata

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
