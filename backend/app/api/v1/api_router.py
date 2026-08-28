from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth, transactions, documents, budgets, goals, analytics, advisor, reports, subscriptions
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions & Ingestion"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents & OCR"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
api_router.include_router(goals.router, prefix="/goals", tags=["Financial Goals & SIP"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics, Anomaly & Forecasting"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions & Recurring Payments"])
api_router.include_router(advisor.router, prefix="/advisor", tags=["AI Advisor & Multi-Guru"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports & Exports"])
