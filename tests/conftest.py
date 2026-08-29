import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "testing"

import pytest
import pytest_asyncio
from backend.app.core.database import engine, Base

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
