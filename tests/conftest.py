import pytest
import pytest_asyncio
from backend.app.core.database import engine, Base
from backend.app.models import (
    User, Profile, Merchant, Category, CategoryRule,
    TransactionSource, Transaction, Budget, BudgetCategory,
    FinancialGoal, GoalContribution, FinancialDocument, DocumentChunk,
    GuruProfile, GuruPrinciple, AdviceSession, Recommendation,
    Subscription, Anomaly, FinancialScore, AuditLog, ChatSession, ChatMessage
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
