from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.app.models.budget import Budget
from backend.app.repositories.base import BaseRepository

class BudgetRepository(BaseRepository[Budget]):
    def __init__(self):
        super().__init__(Budget)

    async def get_user_budgets(self, db: AsyncSession, user_id: str) -> List[Budget]:
        result = await db.execute(
            select(Budget).options(selectinload(Budget.category)).filter(Budget.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_category(self, db: AsyncSession, user_id: str, category_id: str) -> Optional[Budget]:
        result = await db.execute(
            select(Budget).filter(Budget.user_id == user_id, Budget.category_id == category_id)
        )
        return result.scalars().first()

budget_repository = BudgetRepository()
