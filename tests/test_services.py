import pytest
import uuid
from datetime import date
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.schemas.auth import UserRegister, UserLogin
from backend.app.schemas.transaction import TransactionCreate
from backend.app.services.auth_service import auth_service
from backend.app.services.transaction_service import transaction_service

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_auth_service():
    await init_db()
    async with AsyncSessionLocal() as db:
        unique_email = f"serviceuser_{uuid.uuid4().hex[:8]}@finsight.ai"
        reg_payload = UserRegister(
            email=unique_email,
            password="SecureServicePass123!",
            full_name="Service Layer User",
            preferred_currency="INR",
            monthly_income=90000.0
        )
        token_out = await auth_service.register_user(db, reg_payload)
        assert token_out.access_token is not None
        assert token_out.email == unique_email

        # Authenticate
        login_payload = UserLogin(email=unique_email, password="SecureServicePass123!")
        login_out = await auth_service.authenticate_user(db, login_payload)
        assert login_out.access_token is not None
        assert login_out.user_id == token_out.user_id

@pytest.mark.asyncio
async def test_transaction_service():
    async with AsyncSessionLocal() as db:
        unique_email = f"txuser_{uuid.uuid4().hex[:8]}@finsight.ai"
        reg_payload = UserRegister(
            email=unique_email,
            password="SecureServicePass123!",
            full_name="Tx Service User"
        )
        user_auth = await auth_service.register_user(db, reg_payload)

        tx_in = TransactionCreate(
            amount=420.0,
            transaction_type="debit",
            transaction_date=date.today(),
            description="Swiggy Food Order",
            payment_method="UPI"
        )
        created_tx = await transaction_service.create_transaction(db, user_auth.user_id, tx_in)
        assert created_tx is not None
        assert created_tx.amount == 420.0
        # Automatically categorized to Food & Dining or Food
        assert created_tx.category is not None
        assert created_tx.category.name in ["Food", "Food & Dining"]
