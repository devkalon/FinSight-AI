from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.goal import FinancialGoal
from backend.app.repositories.base import BaseRepository

class GoalRepository(BaseRepository[FinancialGoal]):
    def __init__(self):
        super().__init__(FinancialGoal)

    async def get_user_goals(self, db: AsyncSession, user_id: str) -> List[FinancialGoal]:
        result = await db.execute(
            select(FinancialGoal).filter(FinancialGoal.user_id == user_id).order_by(FinancialGoal.target_date.asc())
        )
        return result.scalars().all()

    async def get_by_id_and_user(self, db: AsyncSession, id: str, user_id: str) -> Optional[FinancialGoal]:
        result = await db.execute(
            select(FinancialGoal).filter(FinancialGoal.id == id, FinancialGoal.user_id == user_id)
        )
        return result.scalars().first()

goal_repository = GoalRepository()
