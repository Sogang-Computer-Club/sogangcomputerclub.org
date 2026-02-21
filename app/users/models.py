"""
User database model (SQLAlchemy Table).
"""

import sqlalchemy
from ..core.database import metadata

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column(
        "email", sqlalchemy.String(255), unique=True, nullable=False, index=True
    ),
    sqlalchemy.Column("password_hash", sqlalchemy.String(512), nullable=False),
    sqlalchemy.Column("name", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("student_id", sqlalchemy.String(20), unique=True, nullable=True),
    sqlalchemy.Column(
        "is_active",
        sqlalchemy.Boolean,
        nullable=False,
        default=True,
        server_default="1",
    ),
    sqlalchemy.Column(
        "is_admin",
        sqlalchemy.Boolean,
        nullable=False,
        default=False,
        server_default="0",
    ),
    sqlalchemy.Column(
        "created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()
    ),
    sqlalchemy.Column(
        "updated_at",
        sqlalchemy.DateTime,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)
