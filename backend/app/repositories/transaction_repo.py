import math
from typing import List, Optional, Tuple
from datetime import date
from decimal import Decimal
from sqlalchemy import func, or_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.app.models.transaction import Transaction
from backend.app.repositories.base import BaseRepository

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    async def get_with_filters_paginated(
        self,
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        category_id: Optional[str] = None,
        merchant_name: Optional[str] = None,
        transaction_type: Optional[str] = None,
        payment_method: Optional[str] = None,
        source: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = "transaction_date", # 'transaction_date', 'amount', 'merchant_name', 'created_at'
        sort_order: str = "desc" # 'asc', 'desc'
    ) -> Tuple[List[Transaction], int]:
        # Base filter condition
        filters = [Transaction.user_id == user_id, Transaction.is_deleted == False]

        if search:
            search_pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    Transaction.description.ilike(search_pattern),
                    Transaction.merchant_name.ilike(search_pattern),
                    Transaction.notes.ilike(search_pattern)
                )
            )

        if category_id:
            filters.append(Transaction.category_id == category_id)

        if merchant_name:
            filters.append(Transaction.merchant_name.ilike(f"%{merchant_name.strip()}%"))

        if transaction_type:
            filters.append(Transaction.transaction_type == transaction_type.lower())

        if payment_method:
            filters.append(Transaction.payment_method.ilike(payment_method.strip()))

        if source:
            filters.append(Transaction.source == source.lower())

        if start_date:
            filters.append(Transaction.transaction_date >= start_date)

        if end_date:
            filters.append(Transaction.transaction_date <= end_date)

        if min_amount is not None:
            filters.append(Transaction.amount >= Decimal(str(min_amount)))

        if max_amount is not None:
            filters.append(Transaction.amount <= Decimal(str(max_amount)))

        # 1. Count query
        count_query = select(func.count()).select_from(Transaction).filter(*filters)
        count_res = await db.execute(count_query)
        total_count = count_res.scalar_one()

        # 2. Main query with sorting & pagination
        query = select(Transaction).options(selectinload(Transaction.category)).filter(*filters)

        # Sorting logic
        sort_column = Transaction.transaction_date
        if sort_by == "amount":
            sort_column = Transaction.amount
        elif sort_by == "merchant_name":
            sort_column = Transaction.merchant_name
        elif sort_by == "created_at":
            sort_column = Transaction.created_at

        order_fn = desc if sort_order.lower() == "desc" else asc
        query = query.order_by(order_fn(sort_column), desc(Transaction.created_at))

        # Pagination
        offset = max(0, (page - 1) * page_size)
        query = query.offset(offset).limit(page_size)

        result = await db.execute(query)
        items = result.scalars().all()
        return items, total_count

    async def get_with_filters(
        self,
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Transaction]:
        query = select(Transaction).options(selectinload(Transaction.category)).filter(
            Transaction.user_id == user_id,
            Transaction.is_deleted == False
        )
        
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        query = query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_id_and_user(self, db: AsyncSession, id: str, user_id: str) -> Optional[Transaction]:
        result = await db.execute(
            select(Transaction).options(selectinload(Transaction.category)).filter(
                Transaction.id == id,
                Transaction.user_id == user_id,
                Transaction.is_deleted == False
            )
        )
        return result.scalars().first()

    async def create_batch(self, db: AsyncSession, transactions: List[Transaction]) -> List[Transaction]:
        for tx in transactions:
            db.add(tx)
        await db.commit()
        return transactions

transaction_repository = TransactionRepository()
