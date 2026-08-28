import pytest
import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import User, Profile
from backend.app.models.merchant import Merchant
from backend.app.models.category import Category, CategoryRule
from backend.app.models.transaction import TransactionSource, Transaction
from backend.app.models.budget import Budget, BudgetCategory
from backend.app.models.goal import FinancialGoal, GoalContribution
from backend.app.models.document import FinancialDocument, DocumentChunk
from backend.app.models.guru import GuruProfile, GuruPrinciple, AdviceSession, Recommendation
from backend.app.models.subscription import Subscription
from backend.app.models.anomaly import Anomaly
from backend.app.models.financial_score import FinancialScore
from backend.app.models.audit_log import AuditLog
from backend.app.core.seed import seed_database
from backend.app.core.security import get_password_hash

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_full_normalized_schema_models():
    await init_db()
    async with AsyncSessionLocal() as db:
        unique_email = f"dbtest_{uuid.uuid4().hex[:8]}@finsight.ai"
        
        # 1. User & Profile
        user = User(
            email=unique_email,
            hashed_password=get_password_hash("TestPass123!"),
            is_active=True,
            is_verified=True
        )
        db.add(user)
        await db.flush()
        assert len(user.id) == 36 # Valid UUID

        profile = Profile(
            user_id=user.id,
            full_name="Normalized User",
            monthly_income=Decimal("95000.75"), # Exact Decimal precision
            preferred_currency="INR"
        )
        db.add(profile)
        await db.flush()
        assert profile.monthly_income == Decimal("95000.75")

        # 2. Category & Merchant
        cat = Category(
            user_id=user.id,
            name="Dining & Food",
            group_type="Want",
            color="#F59E0B"
        )
        db.add(cat)
        await db.flush()

        merchant = Merchant(
            name="Swiggy Delivery",
            normalized_name=f"swiggy_{uuid.uuid4().hex[:6]}",
            default_category_id=cat.id
        )
        db.add(merchant)
        await db.flush()

        # 3. Transaction Source & Transaction (with Decimal precision)
        source = TransactionSource(
            user_id=user.id,
            source_name="ICICI Salary Account",
            source_type="bank_pdf"
        )
        db.add(source)
        await db.flush()

        tx = Transaction(
            user_id=user.id,
            source_id=source.id,
            category_id=cat.id,
            merchant_id=merchant.id,
            amount=Decimal("489.50"), # Money stored as exact Decimal
            currency="INR",
            transaction_type="debit",
            transaction_date=date.today(),
            description="Swiggy Biryani Dinner",
            confidence_score=Decimal("0.9500")
        )
        db.add(tx)
        await db.flush()
        assert tx.amount == Decimal("489.50")
        assert tx.confidence_score == Decimal("0.9500")

        # 4. Budget & Budget Category
        budget = Budget(
            user_id=user.id,
            name="Household Budget",
            total_limit=Decimal("40000.00"),
            alert_threshold_percentage=80
        )
        db.add(budget)
        await db.flush()

        b_cat = BudgetCategory(
            budget_id=budget.id,
            category_id=cat.id,
            allocated_limit=Decimal("12000.00")
        )
        db.add(b_cat)
        await db.flush()

        # 5. Financial Goal & Contribution
        goal = FinancialGoal(
            user_id=user.id,
            title="House Down Payment",
            target_amount=Decimal("1500000.00"),
            current_amount=Decimal("250000.00"),
            target_date=date(2028, 12, 31)
        )
        db.add(goal)
        await db.flush()

        contrib = GoalContribution(
            goal_id=goal.id,
            user_id=user.id,
            amount=Decimal("25000.00")
        )
        db.add(contrib)
        await db.flush()

        # 6. Financial Document & Chunk
        doc = FinancialDocument(
            user_id=user.id,
            filename="August_Statement.pdf",
            file_type="bank_statement_pdf",
            file_size_bytes=102400,
            storage_path="/uploads/statements/sample.pdf"
        )
        db.add(doc)
        await db.flush()

        chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            content="Summary of account deposits and debits for August."
        )
        db.add(chunk)
        await db.flush()

        # 7. Guru Profile, Principle, Advice Session & Recommendation
        guru = GuruProfile(
            guru_code=f"buffett_{uuid.uuid4().hex[:6]}",
            name="Warren Buffett",
            title="Value Investor",
            core_mantra="Never lose money.",
            philosophy_description="Value and patience."
        )
        db.add(guru)
        await db.flush()

        principle = GuruPrinciple(
            guru_id=guru.id,
            principle_order=1,
            title="Compounding",
            description="Compounding works over long horizons."
        )
        db.add(principle)
        await db.flush()

        session = AdviceSession(
            user_id=user.id,
            guru_id=guru.id,
            title="Portfolio Strategy Session"
        )
        db.add(session)
        await db.flush()

        rec = Recommendation(
            session_id=session.id,
            user_id=user.id,
            guru_id=guru.id,
            topic="Index Fund SIP",
            recommendation_text="Allocate 20% of monthly income into broad index funds.",
            estimated_savings_impact=Decimal("5000.00")
        )
        db.add(rec)
        await db.flush()

        # 8. Subscription, Anomaly, Financial Score & Audit Log
        sub = Subscription(
            user_id=user.id,
            service_name="Netflix Premium",
            amount=Decimal("649.00"),
            next_billing_date=date.today()
        )
        db.add(sub)
        await db.flush()

        anomaly = Anomaly(
            user_id=user.id,
            transaction_id=tx.id,
            anomaly_type="spend_spike",
            severity="high",
            description="Unusual spike in dining spend",
            z_score=Decimal("2.850")
        )
        db.add(anomaly)
        await db.flush()

        score = FinancialScore(
            user_id=user.id,
            composite_score=85,
            rating="Excellent",
            emergency_fund_score=22,
            savings_rate_score=21,
            budget_adherence_score=21,
            debt_and_burn_score=21
        )
        db.add(score)
        await db.flush()

        log = AuditLog(
            user_id=user.id,
            action="transaction_created",
            entity_type="Transaction",
            entity_id=tx.id
        )
        db.add(log)
        await db.commit()

        # Verify query retrieval
        res_tx = await db.execute(select(Transaction).filter(Transaction.id == tx.id))
        fetched_tx = res_tx.scalars().first()
        assert fetched_tx is not None
        assert fetched_tx.amount == Decimal("489.50")
        assert fetched_tx.is_deleted is False

@pytest.mark.asyncio
async def test_database_seeder():
    await seed_database()
    async with AsyncSessionLocal() as db:
        res_gurus = await db.execute(select(GuruProfile))
        gurus = res_gurus.scalars().all()
        assert len(gurus) >= 4

        res_merchants = await db.execute(select(Merchant))
        merchants = res_merchants.scalars().all()
        assert len(merchants) >= 5
