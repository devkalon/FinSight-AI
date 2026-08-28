import math
from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from backend.app.models.transaction import Transaction
from backend.app.models.category import CategoryRule
from backend.app.schemas.transaction import (
    TransactionCreate, TransactionUpdate, BatchTransactionCreate,
    PaginatedTransactionResponse, TransactionOut
)
from backend.app.repositories.transaction_repo import transaction_repository
from backend.app.repositories.category_repo import category_repository
from backend.app.services.ml.categorizer import expense_categorizer

class TransactionService:
    async def get_transactions_paginated(
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
        sort_by: str = "transaction_date",
        sort_order: str = "desc"
    ) -> PaginatedTransactionResponse:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))

        items, total_count = await transaction_repository.get_with_filters_paginated(
            db=db,
            user_id=user_id,
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

        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 1

        return PaginatedTransactionResponse(
            items=[TransactionOut.model_validate(item) for item in items],
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    async def get_transactions(
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
        return await transaction_repository.get_with_filters(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit,
            category_id=category_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date
        )

    async def get_transaction_by_id(self, db: AsyncSession, user_id: str, tx_id: str) -> Transaction:
        tx = await transaction_repository.get_by_id_and_user(db, tx_id, user_id)
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or access denied"
            )
        return tx

    async def create_transaction(self, db: AsyncSession, user_id: str, tx_in: TransactionCreate) -> Transaction:
        user_rules = await category_repository.get_user_rules(db, user_id)

        cat_id = tx_in.category_id
        if not cat_id:
            suggested_cat = expense_categorizer.categorize(tx_in.description, user_rules=user_rules)
            categories = await category_repository.get_user_categories(db, user_id)
            for c in categories:
                c_name = c.name.lower()
                s_name = suggested_cat.lower()
                if c_name == s_name or s_name in c_name or c_name in s_name:
                    cat_id = c.id
                    break
            if not cat_id and categories:
                cat_id = categories[0].id

        new_tx = Transaction(
            user_id=user_id,
            category_id=cat_id,
            amount=tx_in.amount,
            currency=tx_in.currency or "INR",
            transaction_type=tx_in.transaction_type,
            transaction_date=tx_in.transaction_date,
            description=tx_in.description,
            merchant_name=tx_in.merchant_name,
            subcategory=tx_in.subcategory,
            payment_method=tx_in.payment_method or "UPI",
            source=tx_in.source or "manual",
            confidence_score=tx_in.confidence_score if tx_in.confidence_score is not None else 1.0,
            is_subscription=tx_in.is_subscription or False,
            notes=tx_in.notes,
            extra_metadata=tx_in.extra_metadata
        )
        db.add(new_tx)
        await db.commit()
        return await transaction_repository.get_by_id_and_user(db, new_tx.id, user_id)

    async def batch_create(self, db: AsyncSession, user_id: str, batch_in: BatchTransactionCreate) -> List[Transaction]:
        categories = await category_repository.get_user_categories(db, user_id)
        user_cats = {c.name.lower(): c.id for c in categories}
        user_rules = await category_repository.get_user_rules(db, user_id)

        tx_models = []
        for item in batch_in.transactions:
            cat_id = item.category_id
            if not cat_id:
                suggested_cat = expense_categorizer.categorize(item.description, user_rules=user_rules)
                cat_id = user_cats.get(suggested_cat.lower())

            tx = Transaction(
                user_id=user_id,
                category_id=cat_id,
                amount=item.amount,
                currency=item.currency or "INR",
                transaction_type=item.transaction_type,
                transaction_date=item.transaction_date,
                description=item.description,
                merchant_name=item.merchant_name,
                subcategory=item.subcategory,
                payment_method=item.payment_method or "UPI",
                source=item.source or "batch",
                confidence_score=item.confidence_score if item.confidence_score is not None else 1.0,
                is_subscription=item.is_subscription or False,
                notes=item.notes,
                extra_metadata=item.extra_metadata
            )
            tx_models.append(tx)

        await transaction_repository.create_batch(db, tx_models)
        return await transaction_repository.get_with_filters(db=db, user_id=user_id, limit=len(tx_models))

    async def update_transaction(self, db: AsyncSession, user_id: str, tx_id: str, tx_update: TransactionUpdate) -> Transaction:
        tx = await transaction_repository.get_by_id_and_user(db, tx_id, user_id)
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or access denied"
            )

        if tx_update.amount is not None:
            tx.amount = tx_update.amount
        if tx_update.currency is not None:
            tx.currency = tx_update.currency
        if tx_update.transaction_type is not None:
            tx.transaction_type = tx_update.transaction_type
        if tx_update.transaction_date is not None:
            tx.transaction_date = tx_update.transaction_date
        if tx_update.description is not None:
            tx.description = tx_update.description
        if tx_update.merchant_name is not None:
            tx.merchant_name = tx_update.merchant_name
        if tx_update.subcategory is not None:
            tx.subcategory = tx_update.subcategory
        if tx_update.payment_method is not None:
            tx.payment_method = tx_update.payment_method
        if tx_update.source is not None:
            tx.source = tx_update.source
        if tx_update.category_id is not None:
            tx.category_id = tx_update.category_id
        if tx_update.confidence_score is not None:
            tx.confidence_score = tx_update.confidence_score
        if tx_update.is_subscription is not None:
            tx.is_subscription = tx_update.is_subscription
        if tx_update.notes is not None:
            tx.notes = tx_update.notes
        if tx_update.extra_metadata is not None:
            tx.extra_metadata = tx_update.extra_metadata

        return await transaction_repository.update(db, tx)

    async def delete_transaction(self, db: AsyncSession, user_id: str, tx_id: str) -> bool:
        tx = await transaction_repository.get_by_id_and_user(db, tx_id, user_id)
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or access denied"
            )
        return await transaction_repository.delete(db, tx.id)

transaction_service = TransactionService()
