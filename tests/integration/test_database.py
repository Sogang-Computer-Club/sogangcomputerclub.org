import pytest
import asyncio
import asyncpg
import os


@pytest.mark.asyncio
async def test_postgres_connection():
    """Test connection to PostgreSQL database"""
    try:
        connection = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5433")),
            user=os.getenv("POSTGRES_USER", "memo_user"),
            password=os.getenv("POSTGRES_PASSWORD", "phoenix"),
            database=os.getenv("POSTGRES_DB", "memo_app")
        )

        assert connection is not None

        result = await connection.fetchval("SELECT 1")
        assert result == 1

        await connection.close()

    except Exception as e:
        pytest.fail(f"Failed to connect to PostgreSQL: {e}")


@pytest.mark.asyncio
async def test_postgres_database_exists():
    """Test that the memo_app database exists"""
    try:
        connection = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5433")),
            user=os.getenv("POSTGRES_USER", "memo_user"),
            password=os.getenv("POSTGRES_PASSWORD", "phoenix"),
            database="postgres"
        )

        result = await connection.fetchval(f"SELECT datname FROM pg_database WHERE datname = '{os.getenv('POSTGRES_DB', 'memo_app')}'")
        assert result == os.getenv("POSTGRES_DB", "memo_app")

        await connection.close()

    except Exception as e:
        pytest.fail(f"Failed to verify database exists: {e}")


@pytest.mark.asyncio
async def test_postgres_memos_table_exists():
    """Test that the memos table exists"""
    try:
        connection = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5433")),
            user=os.getenv("POSTGRES_USER", "memo_user"),
            password=os.getenv("POSTGRES_PASSWORD", "phoenix"),
            database=os.getenv("POSTGRES_DB", "memo_app")
        )

        result = await connection.fetchval(
            "SELECT to_regclass('public.memos')"
        )
        assert result == 'memos'

        await connection.close()

    except Exception as e:
        pytest.fail(f"Failed to verify memos table exists: {e}")


@pytest.mark.asyncio
async def test_postgres_memos_table_structure():
    """Test the structure of the memos table"""
    try:
        connection = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5433")),
            user=os.getenv("POSTGRES_USER", "memo_user"),
            password=os.getenv("POSTGRES_PASSWORD", "phoenix"),
            database=os.getenv("POSTGRES_DB", "memo_app")
        )

        rows = await connection.fetch(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'memos'"
        )

        column_names = [row['column_name'] for row in rows]

        expected_columns = [
            'id', 'title', 'content', 'tags', 'priority',
            'category', 'is_archived', 'is_favorite', 'author',
            'created_at', 'updated_at'
        ]

        for expected_col in expected_columns:
            assert expected_col in column_names, f"Column {expected_col} not found in memos table"

        await connection.close()

    except Exception as e:
        pytest.fail(f"Failed to verify memos table structure: {e}")


@pytest.mark.asyncio
async def test_postgres_insert_and_retrieve():
    """Test inserting and retrieving data from memos table"""
    try:
        connection = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5433")),
            user=os.getenv("POSTGRES_USER", "memo_user"),
            password=os.getenv("POSTGRES_PASSWORD", "phoenix"),
            database=os.getenv("POSTGRES_DB", "memo_app")
        )

        # Insert test data
        await connection.execute(
            """
            INSERT INTO memos (title, content, priority)
            VALUES ($1, $2, $3)
            """,
            "Integration Test Memo", "This is a test memo for integration testing", 2
        )

        # Retrieve the inserted data
        row = await connection.fetchrow(
            """
            SELECT title, content, priority
            FROM memos
            WHERE title = $1
            """,
            "Integration Test Memo"
        )

        assert row is not None
        assert row['title'] == "Integration Test Memo"
        assert row['content'] == "This is a test memo for integration testing"
        assert row['priority'] == 2

        # Clean up - delete the test data
        await connection.execute(
            "DELETE FROM memos WHERE title = $1",
            "Integration Test Memo"
        )

        await connection.close()

    except Exception as e:
        pytest.fail(f"Failed to insert and retrieve data: {e}")
