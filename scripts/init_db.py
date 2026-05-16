"""初始化数据库并写入种子数据"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database.engine import init_db, close_db
from src.database.seed import seed_database


async def main() -> None:
    start = time.perf_counter()

    print("[1/3] Creating database tables...")
    await init_db()
    print("      [ok] Tables ready")

    print("[2/3] Writing seed data...")
    await seed_database()
    print("      [ok] Seed data written")

    print("[3/3] Closing database connection...")
    await close_db()

    elapsed = time.perf_counter() - start
    print(f"\n[ok] Database initialized ({elapsed:.2f}s)")
    print("  File: data/shopagent.db")


if __name__ == "__main__":
    asyncio.run(main())
