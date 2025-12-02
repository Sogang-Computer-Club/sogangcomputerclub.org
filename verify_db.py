import asyncio
import asyncpg
import os

async def main():
    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5433,
            user="admin",
            password="82292",
            database="sgcc-backend-db"
        )
        print("Connection successful!")
        await conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5433,
            user="memo_user",
            password="82292",
            database="memo_app"
        )
        print("Connection successful with 82292!")
        await conn.close()
    except Exception as e:
        print(f"Connection failed with 82292: {e}")

    try:
        conn = await asyncpg.connect(
            host="localhost",
            port=5433,
            user="memo_user",
            password="phoenix",
            database="memo_app"
        )
        print("Connection successful with phoenix!")
        await conn.close()
    except Exception as e:
        print(f"Connection failed with phoenix: {e}")

if __name__ == "__main__":
    asyncio.run(main())
