import os
import tempfile

import pytest

# 测试用临时文件数据库（避免 :memory: 跨连接不共享问题）
_test_db_path = os.path.join(tempfile.gettempdir(), "shopagent_test.db")

# 清理之前的测试数据库
if os.path.exists(_test_db_path):
    os.remove(_test_db_path)

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_test_db_path}"

from src.database.engine import get_engine, get_session, get_session_factory, init_db
from src.database.models import Base
from src.database.seed import seed_database

# 重用引擎和 session
_engine = None
_seeded = False


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_test_db():
    global _seeded
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not _seeded:
        await seed_database()
        _seeded = True
    yield


@pytest.fixture(scope="session", autouse=True)
async def cleanup():
    yield
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
    if os.path.exists(_test_db_path):
        os.remove(_test_db_path)
