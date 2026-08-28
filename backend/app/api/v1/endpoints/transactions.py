from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.category import Category, CategoryRule
from backend.app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, TransactionOut,
    BatchTransactionCreate, PaginatedTransactionResponse
)
from backend.app.schemas.category import CategoryOut, CategoryCreate, CategoryRuleCreate, CategoryRuleOut
from backend.app.services.transaction_service import transaction_service
from backend.app.repositories.category_repo import category_repository
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=PaginatedTransactionResponse)
async def list_transactions(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search keyword in description, merchant or notes"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    merchant_name: Optional[str] = Query(None, description="Filter by merchant name"),
    transaction_type: Optional[str] = Query(None, description="Filter by 'debit', 'credit' or 'transfer'"),
    payment_method: Optional[str] = Query(None, description="Filter by payment method (UPI, Card, etc)"),
    source: Optional[str] = Query(None, description="Filter by source (manual, ocr, pdf, csv)"),
    start_date: Optional[date] = Query(None, description="Filter transactions on or after this date"),
    end_date: Optional[date] = Query(None, description="Filter transactions on or before this date"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum transaction amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum transaction amount"),
    sort_by: str = Query("transaction_date", description="Sort by 'transaction_date', 'amount', 'merchant_name', or 'created_at'"),
    sort_order: str = Query("desc", description="Sort order 'asc' or 'desc'"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await transaction_service.get_transactions_paginated(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        merchant_name=merchant_name,
        transaction_type=transaction_type,
        payment_method=payment_method,
        source=source,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
        sort_by=sort_by,
        sort_order=sort_order
    )

# Static paths precede dynamic path parameter routes
@router.get("/categories", response_model=List[CategoryOut])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await category_repository.get_user_categories(db, current_user.id)

@router.post("/categories", response_model=CategoryOut)
async def create_category(
    cat_in: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_cat = Category(
        user_id=current_user.id,
        name=cat_in.name,
        group_type=cat_in.group_type or "Need",
        icon=cat_in.icon or "Tag",
        color=cat_in.color or "#6366F1",
        is_custom=True
    )
    return await category_repository.create(db, new_cat)

@router.post("/rules/learn", response_model=CategoryRuleOut)
async def create_learning_rule(
    rule_in: CategoryRuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rule = CategoryRule(
        user_id=current_user.id,
        keyword_pattern=rule_in.keyword_pattern.lower().strip(),
        category_id=rule_in.category_id,
        confidence_score=1.0
    )
    return await category_repository.add_rule(db, rule)

@router.post("/batch", response_model=List[TransactionOut])
async def batch_create_transactions(
    batch_in: BatchTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await transaction_service.batch_create(db, current_user.id, batch_in)

@router.post("/", response_model=TransactionOut)
async def create_transaction(
    tx_in: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await transaction_service.create_transaction(db, current_user.id, tx_in)

# Dynamic {tx_id} routes
@router.get("/{tx_id}", response_model=TransactionOut)
async def get_transaction(
    tx_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await transaction_service.get_transaction_by_id(db, current_user.id, tx_id)

@router.put("/{tx_id}", response_model=TransactionOut)
async def update_transaction(
    tx_id: str,
    tx_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await transaction_service.update_transaction(db, current_user.id, tx_id, tx_update)

@router.delete("/{tx_id}")
async def delete_transaction(
    tx_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await transaction_service.delete_transaction(db, current_user.id, tx_id)
    return {"message": "Transaction deleted successfully"}
