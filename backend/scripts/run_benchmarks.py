import sys
import os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import time
import uuid
import math
import random
import asyncio
import numpy as np
from datetime import date, timedelta
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.app.models.base import Base
from backend.app.models.user import User, Profile
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.models.budget import Budget
from backend.app.services.financial_analytics import financial_analytics_engine
from backend.app.services.financial_health import financial_health_engine
from backend.app.services.ai.rag_engine import rag_engine
from backend.app.services.ai.agent import financial_advisor_agent
from backend.app.services.ingestion.ocr_engine import ocr_engine
from backend.app.services.ingestion.csv_parser import csv_parser

def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    return float(np.percentile(data, p))

async def run_benchmark_for_scale(scale: int, num_runs: int = 30) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"🚀 INITIALIZING BENCHMARK SCALE: {scale:,} TRANSACTIONS")
    print(f"=======================================================")

    db_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        user_id = str(uuid.uuid4())
        user = User(id=user_id, email=f"bench_{scale}@finsight.ai", hashed_password="pw", is_active=True)
        profile = Profile(id=str(uuid.uuid4()), user_id=user_id, full_name="Bench User", monthly_income=150000.0)
        
        cat_food = Category(id="cat_b_1", name="Food & Dining", group_type="expense", color="#EF4444")
        cat_rent = Category(id="cat_b_2", name="Housing & Rent", group_type="expense", color="#3B82F6")
        cat_salary = Category(id="cat_b_3", name="Salary", group_type="income", color="#10B981")
        cat_invest = Category(id="cat_b_4", name="Investments", group_type="expense", color="#8B5CF6")
        cat_util = Category(id="cat_b_5", name="Utilities", group_type="expense", color="#F59E0B")
        
        session.add_all([user, profile, cat_food, cat_rent, cat_salary, cat_invest, cat_util])
        await session.commit()

        # 1. Generate Synthetic Transactions
        today = date.today()
        print(f"Generating {scale:,} synthetic transactions in batches...")
        t_gen_start = time.time()
        
        chunk_size = 5000
        cats = ["cat_b_1", "cat_b_2", "cat_b_4", "cat_b_5"]
        
        for batch_i in range(0, scale, chunk_size):
            tx_batch = []
            for j in range(chunk_size):
                idx = batch_i + j
                is_credit = (idx % 12 == 0)
                tx_batch.append(Transaction(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    category_id="cat_b_3" if is_credit else random.choice(cats),
                    amount=random.uniform(500.0, 50000.0) if is_credit else random.uniform(50.0, 3500.0),
                    currency="INR",
                    transaction_type="credit" if is_credit else "debit",
                    transaction_date=today - timedelta(days=idx % 365),
                    description=f"Synthetic Transaction #{idx}",
                    merchant_name=f"Merchant_{idx % 100}",
                    payment_method=random.choice(["UPI", "Credit Card", "Net Banking"]),
                    is_deleted=False
                ))
            session.add_all(tx_batch)
            await session.commit()

        t_gen_duration = time.time() - t_gen_start
        print(f"✓ {scale:,} rows inserted in {t_gen_duration:.2f}s (Throughput: {int(scale/t_gen_duration):,} tx/sec)")

        # 2. Measure Database Query Latency (Paginated Ledger Query)
        print(f"\nMeasuring Database Ledger Query Latency ({num_runs} iterations)...")
        query_latencies = []
        for _ in range(num_runs):
            t0 = time.perf_counter()
            from sqlalchemy import select
            q = select(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False
            ).order_by(Transaction.transaction_date.desc()).limit(50)
            res = await session.execute(q)
            _ = res.scalars().all()
            t1 = time.perf_counter()
            query_latencies.append((t1 - t0) * 1000.0)

        # 3. Measure Analytics Calculation Latency (Full Aggregations over dataset)
        print(f"Measuring Analytics Calculation Latency ({num_runs} iterations)...")
        analytics_latencies = []
        for _ in range(num_runs):
            t0 = time.perf_counter()
            _ = await financial_analytics_engine.calculate_summary(
                db=session,
                user_id=user_id,
                start_date=today - timedelta(days=90),
                end_date=today
            )
            t1 = time.perf_counter()
            analytics_latencies.append((t1 - t0) * 1000.0)

        # 4. Measure Dashboard Composite Latency (Summary + Category + Health)
        print(f"Measuring Dashboard API Latency ({num_runs} iterations)...")
        dashboard_latencies = []
        for _ in range(num_runs):
            t0 = time.perf_counter()
            _ = await financial_analytics_engine.get_monthly_summary(session, user_id)
            _ = await financial_analytics_engine.get_spending_by_category(session, user_id)
            _ = await financial_health_engine.calculate_composite_health_score(session, user_id)
            t1 = time.perf_counter()
            dashboard_latencies.append((t1 - t0) * 1000.0)

        # 5. Measure CSV Import Time
        print(f"Measuring CSV Ingestion Latency (1,000 row batch)...")
        csv_latencies = []
        sample_csv_lines = ["Date,Description,Amount,Type\n"] + [
            f"{(today - timedelta(days=i%30)).strftime('%Y-%m-%d')},Test Merchant {i},{random.uniform(50, 2000):.2f},DEBIT\n"
            for i in range(1000)
        ]
        csv_bytes = "".join(sample_csv_lines).encode("utf-8")
        
        for _ in range(10):
            t0 = time.perf_counter()
            parsed, summary = csv_parser.parse_csv_with_summary(csv_bytes, "test_statement.csv")
            t1 = time.perf_counter()
            csv_latencies.append((t1 - t0) * 1000.0)

        # 6. Measure OCR Processing Latency
        print(f"Measuring OCR Ingestion & Fallback Latency...")
        ocr_latencies = []
        import tempfile
        from PIL import Image as PILImage
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
            img = PILImage.new("RGB", (300, 300), color=(255, 255, 255))
            img.save(tmp_img.name)
            tmp_img_path = tmp_img.name

        try:
            for _ in range(15):
                t0 = time.perf_counter()
                _ = ocr_engine.extract_from_image(tmp_img_path, "receipt.png")
                t1 = time.perf_counter()
                ocr_latencies.append((t1 - t0) * 1000.0)
        finally:
            if os.path.exists(tmp_img_path):
                os.remove(tmp_img_path)

        # 7. Measure RAG Retrieval Latency
        print(f"Measuring RAG Semantic Retrieval Latency ({num_runs} iterations)...")
        rag_latencies = []
        for _ in range(num_runs):
            t0 = time.perf_counter()
            _ = await rag_engine.retrieve_user_knowledge(
                db=session,
                user_id=user_id,
                query="What is the compounding return of equity index funds and SIP?",
                top_k=3
            )
            t1 = time.perf_counter()
            rag_latencies.append((t1 - t0) * 1000.0)

        # 8. Measure AI Response Latency (Full Agent LangGraph Pipeline)
        print(f"Measuring AI Advisor LangGraph Execution Latency ({num_runs} iterations)...")
        ai_latencies = []
        for _ in range(num_runs):
            t0 = time.perf_counter()
            _ = await financial_advisor_agent.process_query(
                db=session,
                user_id=user_id,
                user_query="Calculate SIP of ₹15,000 per month for 10 years and check my health score",
                persona="buffett"
            )
            t1 = time.perf_counter()
            ai_latencies.append((t1 - t0) * 1000.0)

    await engine.dispose()

    results = {
        "scale": scale,
        "insert_duration_sec": round(t_gen_duration, 2),
        "db_query": {
            "p50": round(percentile(query_latencies, 50), 2),
            "p95": round(percentile(query_latencies, 95), 2),
            "p99": round(percentile(query_latencies, 99), 2),
        },
        "analytics": {
            "p50": round(percentile(analytics_latencies, 50), 2),
            "p95": round(percentile(analytics_latencies, 95), 2),
            "p99": round(percentile(analytics_latencies, 99), 2),
        },
        "dashboard": {
            "p50": round(percentile(dashboard_latencies, 50), 2),
            "p95": round(percentile(dashboard_latencies, 95), 2),
            "p99": round(percentile(dashboard_latencies, 99), 2),
        },
        "csv_import_1k": {
            "p50": round(percentile(csv_latencies, 50), 2),
            "p95": round(percentile(csv_latencies, 95), 2),
            "p99": round(percentile(csv_latencies, 99), 2),
        },
        "ocr_processing": {
            "p50": round(percentile(ocr_latencies, 50), 2),
            "p95": round(percentile(ocr_latencies, 95), 2),
            "p99": round(percentile(ocr_latencies, 99), 2),
        },
        "rag_retrieval": {
            "p50": round(percentile(rag_latencies, 50), 2),
            "p95": round(percentile(rag_latencies, 95), 2),
            "p99": round(percentile(rag_latencies, 99), 2),
        },
        "ai_response": {
            "p50": round(percentile(ai_latencies, 50), 2),
            "p95": round(percentile(ai_latencies, 95), 2),
            "p99": round(percentile(ai_latencies, 99), 2),
        }
    }

    print(f"\n📊 Benchmark Summary for {scale:,} Transactions:")
    print(f"- DB Query:      P50: {results['db_query']['p50']}ms | P95: {results['db_query']['p95']}ms | P99: {results['db_query']['p99']}ms")
    print(f"- Analytics:     P50: {results['analytics']['p50']}ms | P95: {results['analytics']['p95']}ms | P99: {results['analytics']['p99']}ms")
    print(f"- Dashboard API: P50: {results['dashboard']['p50']}ms | P95: {results['dashboard']['p95']}ms | P99: {results['dashboard']['p99']}ms")
    print(f"- CSV Import:    P50: {results['csv_import_1k']['p50']}ms | P95: {results['csv_import_1k']['p95']}ms | P99: {results['csv_import_1k']['p99']}ms")
    print(f"- OCR Pipeline:  P50: {results['ocr_processing']['p50']}ms | P95: {results['ocr_processing']['p95']}ms | P99: {results['ocr_processing']['p99']}ms")
    print(f"- RAG Retrieval: P50: {results['rag_retrieval']['p50']}ms | P95: {results['rag_retrieval']['p95']}ms | P99: {results['rag_retrieval']['p99']}ms")
    print(f"- AI Response:   P50: {results['ai_response']['p50']}ms | P95: {results['ai_response']['p95']}ms | P99: {results['ai_response']['p99']}ms")

    return results

async def main():
    scales = [10000, 50000, 100000]
    all_results = {}
    for s in scales:
        all_results[s] = await run_benchmark_for_scale(s, num_runs=30)
    
    print("\n=======================================================")
    print("ALL SCALE BENCHMARKS COMPLETE!")
    print("=======================================================")

if __name__ == "__main__":
    asyncio.run(main())
