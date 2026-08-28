import io
from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.budget import Budget
from backend.app.models.goal import FinancialGoal
from backend.app.models.subscription import Subscription
from backend.app.schemas.report import MonthlyReportResponse
from backend.app.services.monthly_report_engine import monthly_report_engine
from backend.app.services.ml.anomaly_detector import anomaly_detector
from backend.app.api.deps import get_current_user

router = APIRouter()

async def _build_report_for_user(user: User, db: AsyncSession, month_str: str) -> MonthlyReportResponse:
    # 1. Fetch transactions
    tx_res = await db.execute(
        select(Transaction)
        .options(selectinload(Transaction.category))
        .filter(Transaction.user_id == user.id, Transaction.is_deleted == False)
        .order_by(Transaction.transaction_date.desc())
    )
    txs = tx_res.scalars().all()
    tx_dicts = [
        {
            "id": t.id,
            "description": t.description,
            "amount": float(t.amount),
            "transaction_type": t.transaction_type,
            "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None,
            "category_name": t.category.name if t.category else "Other"
        }
        for t in txs
    ]

    # 2. Fetch budgets
    b_res = await db.execute(
        select(Budget).options(selectinload(Budget.category)).filter(Budget.user_id == user.id)
    )
    budgets = [
        {
            "category_name": b.category.name if b.category else "Category",
            "monthly_limit": float(b.total_limit),
            "spent_amount": 0.0,
            "spent_percentage": 0.0,
            "is_over_budget": False
        }
        for b in b_res.scalars().all()
    ]

    # 3. Fetch goals
    g_res = await db.execute(
        select(FinancialGoal).filter(FinancialGoal.user_id == user.id)
    )
    goals = [
        {
            "title": g.title,
            "target_amount": float(g.target_amount),
            "current_amount": float(g.current_amount),
            "progress_percentage": round(float(g.current_amount) / float(g.target_amount) * 100.0, 1) if float(g.target_amount) > 0 else 0.0,
            "required_monthly_saving": round(max(float(g.target_amount) - float(g.current_amount), 0) / 6.0, 2),
            "projected_completion_date": g.target_date.strftime("%B %Y")
        }
        for g in g_res.scalars().all()
    ]

    # 4. Fetch anomalies
    anomalies = anomaly_detector.detect_anomalies(tx_dicts)

    # 5. Fetch subscriptions
    s_res = await db.execute(
        select(Subscription).filter(Subscription.user_id == user.id, Subscription.is_deleted == False)
    )
    subscriptions = [
        {
            "service_name": s.service_name,
            "amount": float(s.amount),
            "billing_cycle": s.billing_cycle,
            "annualized_cost": float(s.amount) * (12 if s.billing_cycle == "monthly" else 1)
        }
        for s in s_res.scalars().all()
    ]

    return monthly_report_engine.generate_report(
        month_str=month_str,
        user_name=user.full_name or "Client",
        transactions=tx_dicts,
        budgets=budgets,
        goals=goals,
        anomalies=anomalies,
        subscriptions=subscriptions,
        user_income=float(user.monthly_income or 75000.0),
        currency=user.preferred_currency or "INR"
    )

@router.get("/monthly", response_model=MonthlyReportResponse)
async def get_monthly_financial_report(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format, e.g. 2026-08"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates deterministic AI-assisted monthly financial report covering all 11 core sections:
    1. Executive summary, 2. Income, 3. Spending, 4. Savings, 5. Budget performance,
    6. Goal progress, 7. Anomalies, 8. Recurring expenses, 9. Forecast,
    10. Key observations, 11. Recommended actions.
    """
    target_month = month or date.today().strftime("%Y-%m")
    return await _build_report_for_user(current_user, db, target_month)

@router.get("/monthly/pdf")
async def export_monthly_report_pdf(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format, e.g. 2026-08"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generates and downloads the full 11-section Monthly Financial Intelligence Report in PDF.
    """
    target_month = month or date.today().strftime("%Y-%m")
    report = await _build_report_for_user(current_user, db, target_month)
    pdf_bytes = monthly_report_engine.generate_pdf(report)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=FinSight_Monthly_Report_{target_month}.pdf"}
    )

@router.get("/export/csv")
async def export_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Transaction).options(selectinload(Transaction.category)).filter(Transaction.user_id == current_user.id).order_by(Transaction.transaction_date.desc())
    )
    txs = res.scalars().all()

    csv_output = io.StringIO()
    csv_output.write("Date,Description,Category,Type,Amount,Payment Method,Source\n")

    for t in txs:
        cat_name = t.category.name if t.category else "General"
        clean_desc = t.description.replace(",", " ")
        csv_output.write(f"{t.transaction_date},{clean_desc},{cat_name},{t.transaction_type},{t.amount},{t.payment_method},{t.source}\n")

    return Response(
        content=csv_output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=FinSight_Transactions_{date.today().isoformat()}.csv"}
    )

@router.get("/export/pdf")
async def export_pdf(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    target_month = date.today().strftime("%Y-%m")
    report = await _build_report_for_user(current_user, db, target_month)
    pdf_bytes = monthly_report_engine.generate_pdf(report)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=FinSight_Statement_{date.today().isoformat()}.pdf"}
    )
