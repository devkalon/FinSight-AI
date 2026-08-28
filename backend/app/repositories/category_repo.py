from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.models.category import Category, CategoryRule
from backend.app.repositories.base import BaseRepository

class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

    async def get_user_categories(self, db: AsyncSession, user_id: str) -> List[Category]:
        result = await db.execute(
            select(Category).filter((Category.user_id == user_id) | (Category.user_id == None)).order_by(Category.name.asc())
        )
        return result.scalars().all()

    async def get_user_rules(self, db: AsyncSession, user_id: str) -> List[dict]:
        res = await db.execute(
            select(CategoryRule, Category.name.label("category_name"))
            .join(Category, CategoryRule.category_id == Category.id)
            .filter(CategoryRule.user_id == user_id)
        )
        return [{"keyword_pattern": r.CategoryRule.keyword_pattern, "category_name": r.category_name} for r in res.all()]

    async def add_rule(self, db: AsyncSession, rule: CategoryRule) -> CategoryRule:
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

category_repository = CategoryRepository()
