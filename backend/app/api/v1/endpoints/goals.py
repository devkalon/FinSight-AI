import math
from typing import List
from datetime import date, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.goal import FinancialGoal
from backend.app.schemas.goal import GoalCreate, GoalUpdate, GoalOut, GoalContribute
from backend.app.services.ai.tools import financial_tools
from backend.app.api.deps import get_current_user

router = APIRouter()

def _build_goal_dto(g: FinancialGoal, user_monthly_income: float = 75000.0, currency: str = "INR") -> GoalOut:
    curr = float(g.current_amount)
    targ = float(g.target_amount)
    pct = (curr / targ * 100) if targ > 0 else 0.0
    remaining = max(targ - curr, 0.0)

    today = date.today()
    # Calculate months remaining
    months_remaining = max(
        ((g.target_date.year - today.year) * 12 + (g.target_date.month - today.month)),
        1
    )

    # Dynamic deterministic required monthly saving
    req_monthly_saving = round(remaining / months_remaining, 2)

    # Compound SIP annuity estimate
    annual_rate = float(g.expected_return_rate) if g.expected_return_rate else 12.0
    r = (annual_rate / 100.0) / 12.0
    n = months_remaining
    if r > 0 and n > 0:
        req_sip = round(remaining * r / ((1 + r) * (math.pow(1 + r, n) - 1)), 2)
    else:
        req_sip = req_monthly_saving

    monthly_contrib = float(g.monthly_contribution) if g.monthly_contribution else req_monthly_saving

    # Dynamic projected completion date
    if monthly_contrib > 0 and remaining > 0:
        months_to_complete = math.ceil(remaining / monthly_contrib)
        proj_comp_date = (today + timedelta(days=months_to_complete * 30.5)).strftime("%B %Y")
    elif remaining == 0:
        proj_comp_date = "Achieved"
    else:
        proj_comp_date = g.target_date.strftime("%B %Y")

    is_on_track = (curr >= targ) or (monthly_contrib >= req_monthly_saving * 0.90)

    # Contextual AI recommendation
    if curr >= targ:
        ai_rec = f"Congratulations! You have reached your {g.title} goal of {currency} {targ:,.2f}."
    elif req_monthly_saving <= user_monthly_income * 0.20:
        ai_rec = (
            f"To achieve your {g.title} goal of {currency} {targ:,.2f} by {g.target_date.strftime('%B %Y')}, "
            f"save {currency} {req_monthly_saving:,.2f}/month ({months_remaining} months remaining). "
            f"This represents a comfortable {round(req_monthly_saving/max(user_monthly_income, 1)*100, 1)}% of your monthly income."
        )
    else:
        ai_rec = (
            f"Reaching {currency} {targ:,.2f} by {g.target_date.strftime('%B %Y')} requires "
            f"{currency} {req_monthly_saving:,.2f}/month. Consider extending your target horizon or boosting monthly savings rate."
        )

    return GoalOut(
        id=g.id,
        user_id=g.user_id,
        title=g.title,
        category=g.category,
        target_amount=targ,
        current_amount=curr,
        target_date=g.target_date,
        expected_return_rate=float(g.expected_return_rate) if g.expected_return_rate else 12.0,
        monthly_contribution=monthly_contrib,
        status="achieved" if curr >= targ else g.status,
        progress_percentage=round(min(pct, 100.0), 1),
        remaining_amount=round(remaining, 2),
        months_remaining=months_remaining,
        required_monthly_saving=req_monthly_saving,
        required_monthly_sip=req_sip,
        projected_completion_date=proj_comp_date,
        is_on_track=is_on_track,
        ai_recommendation=ai_rec,
        projected_corpus_at_maturity=targ,
        created_at=g.created_at
    )

@router.get("/", response_model=List[GoalOut])
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(FinancialGoal).filter(FinancialGoal.user_id == current_user.id).order_by(FinancialGoal.target_date.asc())
    )
    goals = res.scalars().all()
    user_inc = float(current_user.monthly_income or 75000.0)
    curr = current_user.preferred_currency or "INR"
    return [_build_goal_dto(g, user_inc, curr) for g in goals]

@router.get("/{goal_id}", response_model=GoalOut)
async def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(FinancialGoal).filter(FinancialGoal.id == goal_id, FinancialGoal.user_id == current_user.id)
    )
    g = res.scalars().first()
    if not g:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or access denied"
        )
    return _build_goal_dto(g, float(current_user.monthly_income or 75000.0), current_user.preferred_currency or "INR")

@router.post("/", response_model=GoalOut)
async def create_goal(
    goal_in: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    goal = FinancialGoal(
        user_id=current_user.id,
        title=goal_in.title,
        category=goal_in.category or "Wealth Creation",
        target_amount=Decimal(str(goal_in.target_amount)),
        current_amount=Decimal(str(goal_in.current_amount or 0.0)),
        target_date=goal_in.target_date,
        expected_return_rate=Decimal(str(goal_in.expected_return_rate or 12.0)),
        monthly_contribution=Decimal(str(goal_in.monthly_contribution or 0.0)),
        status="in_progress"
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return _build_goal_dto(goal, float(current_user.monthly_income or 75000.0), current_user.preferred_currency or "INR")

@router.put("/{goal_id}", response_model=GoalOut)
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(FinancialGoal).filter(FinancialGoal.id == goal_id, FinancialGoal.user_id == current_user.id)
    )
    goal = res.scalars().first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or access denied"
        )

    if goal_update.title is not None:
        goal.title = goal_update.title
    if goal_update.category is not None:
        goal.category = goal_update.category
    if goal_update.target_amount is not None:
        goal.target_amount = Decimal(str(goal_update.target_amount))
    if goal_update.current_amount is not None:
        goal.current_amount = Decimal(str(goal_update.current_amount))
    if goal_update.target_date is not None:
        goal.target_date = goal_update.target_date
    if goal_update.expected_return_rate is not None:
        goal.expected_return_rate = Decimal(str(goal_update.expected_return_rate))
    if goal_update.monthly_contribution is not None:
        goal.monthly_contribution = Decimal(str(goal_update.monthly_contribution))
    if goal_update.status is not None:
        goal.status = goal_update.status

    await db.commit()
    await db.refresh(goal)
    return _build_goal_dto(goal, float(current_user.monthly_income or 75000.0), current_user.preferred_currency or "INR")

@router.post("/{goal_id}/contribute", response_model=GoalOut)
async def contribute_to_goal(
    goal_id: str,
    contribution: GoalContribute,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(FinancialGoal).filter(FinancialGoal.id == goal_id, FinancialGoal.user_id == current_user.id))
    goal = res.scalars().first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or access denied"
        )

    goal.current_amount = Decimal(str(float(goal.current_amount) + contribution.amount))
    if goal.current_amount >= goal.target_amount:
        goal.status = "achieved"

    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return _build_goal_dto(goal, float(current_user.monthly_income or 75000.0), current_user.preferred_currency or "INR")

@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(select(FinancialGoal).filter(FinancialGoal.id == goal_id, FinancialGoal.user_id == current_user.id))
    g = res.scalars().first()
    if not g:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found or access denied"
        )
    await db.delete(g)
    await db.commit()
    return {"message": "Goal deleted successfully"}
