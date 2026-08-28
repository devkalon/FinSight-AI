import pytest
import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import User, Profile
from backend.app.models.category import Category, CategoryRule
from backend.app.models.transaction import Transaction
from backend.app.repositories.user_repo import user_repository
from backend.app.repositories.category_repo import category_repository
from backend.app.repositories.transaction_repo import transaction_repository
from backend.app.core.security import get_password_hash

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_user_repository():
    await init_db()
    async with AsyncSessionLocal() as db:
        unique_email = f"repouser_{uuid.uuid4().hex[:8]}@finsight.ai"
        user = User(
            email=unique_email,
            hashed_password=get_password_hash("SecretPass123!"),
            is_active=True
        )
        created_user = await user_repository.create(db, user)
        assert created_user.id is not None

        profile = Profile(
            user_id=created_user.id,
            full_name="Repository Test User",
            monthly_income=Decimal("75000.00")
        )
        db.add(profile)
        await db.commit()

        fetched_user = await user_repository.get_by_email(db, unique_email)
        assert fetched_user is not None
        assert fetched_user.id == created_user.id

@pytest.mark.asyncio
async def test_category_and_rules_repository():
    async with AsyncSessionLocal() as db:
        user_id = str(uuid.uuid4())
        cat = Category(
            user_id=user_id,
            name=f"Fitness_{uuid.uuid4().hex[:6]}",
            group_type="Need",
            color="#14B8A6",
            is_custom=True
        )
        created_cat = await category_repository.create(db, cat)
        assert created_cat.id is not None

        # Add learning rule
        rule = CategoryRule(
            user_id=user_id,
            keyword_pattern="cult fit",
            category_id=created_cat.id,
            confidence_score=1.0
        )
        created_rule = await category_repository.add_rule(db, rule)
        assert created_rule.id is not None

        rules = await category_repository.get_user_rules(db, user_id)
        assert len(rules) >= 1
        assert rules[0]["keyword_pattern"] == "cult fit"

@pytest.mark.asyncio
async def test_transaction_repository():
    async with AsyncSessionLocal() as db:
        user_id = str(uuid.uuid4())
        tx = Transaction(
            user_id=user_id,
            amount=Decimal("850.00"),
            transaction_type="debit",
            transaction_date=date.today(),
            description="Organic Groceries Store",
            payment_method="UPI"
        )
        created_tx = await transaction_repository.create(db, tx)
        assert created_tx.id is not None

        user_txs = await transaction_repository.get_with_filters(db, user_id=user_id)
        assert len(user_txs) == 1
        assert user_txs[0].amount == Decimal("850.00")
