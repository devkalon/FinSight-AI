import pytest
import pytest_asyncio
import backend.app.models # Registers all 20 models on Base.metadata
from backend.app.core.database import engine, Base
from backend.app.main import clear_rate_limit_store
from backend.app.core.security import clear_revoked_tokens_for_testing

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(autouse=True)
def reset_test_state():
    clear_rate_limit_store()
    clear_revoked_tokens_for_testing()
