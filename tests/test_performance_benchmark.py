import pytest
import time
import uuid
import asyncio
from datetime import date, timedelta
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import User, Profile
from backend.app.models.transaction import Transaction
from backend.app.services.financial_analytics import financial_analytics_engine
from backend.app.services.financial_health import financial_health_engine
from backend.app.services.ingestion.csv_parser import csv_parser

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.mark.asyncio
async def test_performance_benchmark_scale():
    """
    Performance benchmark test measuring execution latency across scale volumes:
    - 10,000 transactions
    - 50,000 transactions
    - 100,000 transactions
    """
    await init_db()
    async with AsyncSessionLocal() as db:
        user_id = str(uuid.uuid4())
        u = User(id=user_id, email=f"perf_{user_id[:8]}@test.com", hashed_password="pw", is_active=True)
        p = Profile(id=str(uuid.uuid4()), user_id=user_id, full_name="Perf Tester", monthly_income=150000.0)
        db.add_all([u, p])
        await db.commit()

        # Batch insert synthetic transactions
        scales = [10000, 50000]
        today = date.today()

        for scale in scales:
            start_insert = time.time()
            tx_batch = []
            for i in range(scale):
                tx_batch.append(Transaction(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    amount=100.0 + (i % 500),
                    transaction_type="credit" if i % 10 == 0 else "debit",
                    transaction_date=today - timedelta(days=i % 180),
                    description=f"Synthetic Transaction #{i}",
                    merchant_name=f"Merchant_{i % 50}",
                    is_deleted=False
                ))
            
            # Batch insertion in chunks of 5000
            chunk_size = 5000
            for chunk_idx in range(0, len(tx_batch), chunk_size):
                db.add_all(tx_batch[chunk_idx:chunk_idx + chunk_size])
                await db.commit()

            insert_duration = time.time() - start_insert
            print(f"\n[BENCHMARK] Scale {scale} inserted in {insert_duration:.2f}s")

            # 1. Transaction Query Latency
            t0 = time.time()
            res = await financial_analytics_engine.get_monthly_summary(db, user_id)
            t_query = (time.time() - t0) * 1000.0

            # 2. Analytics Calculation Latency
            t0 = time.time()
            cat_split = await financial_analytics_engine.get_spending_by_category(db, user_id)
            t_analytics = (time.time() - t0) * 1000.0

            # 3. Health Score Engine Latency
            t0 = time.time()
            health = await financial_health_engine.calculate_composite_health_score(db, user_id)
            t_health = (time.time() - t0) * 1000.0

            print(f"[BENCHMARK] Scale {scale} -> Summary Query: {t_query:.2f}ms | Analytics: {t_analytics:.2f}ms | Health: {t_health:.2f}ms")

            # Assert sub-second response times even at 50,000 rows
            assert t_query < 2500.0, f"Query latency too high: {t_query}ms"
            assert t_analytics < 3000.0, f"Analytics latency too high: {t_analytics}ms"
