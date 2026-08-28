from datetime import date, timedelta
from typing import List, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.transaction import Transaction
from backend.app.models.subscription import Subscription
from backend.app.models.category import Category
from backend.app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionOut,
    SubscriptionDashboardResponse
)
from backend.app.services.ml.subscription_tracker import subscription_tracker
from backend.app.api.deps import get_current_user

router = APIRouter()

def _to_subscription_dto(s: Subscription) -> SubscriptionOut:
    amt = float(s.amount)
    annualized = subscription_tracker.calculate_annualized_cost(amt, s.billing_cycle)
    return SubscriptionOut(
        id=s.id,
        user_id=s.user_id,
        service_name=s.service_name,
        amount=amt,
        currency=s.currency or "INR",
        billing_cycle=s.billing_cycle or "monthly",
        recurring_type=s.recurring_type or "monthly_subscription",
        annualized_cost=annualized,
        confidence=float(s.confidence or 0.90),
        status=s.status or "confirmed",
        last_paid_date=s.last_paid_date,
        next_billing_date=s.next_billing_date or (date.today() + timedelta(days=14)),
        is_active=s.is_active,
        category_name=s.category.name if s.category else "Subscriptions",
        created_at=s.created_at
    )

@router.get("/", response_model=SubscriptionDashboardResponse)
async def get_subscriptions_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns full subscriptions and recurring payments dashboard:
    - Active & pending detected subscriptions
    - Total monthly and annualized recurring burn
    - Categorized recurring breakdown
    """
    res = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.category))
        .filter(Subscription.user_id == current_user.id, Subscription.is_deleted == False)
        .order_by(Subscription.next_billing_date.asc())
    )
    subs = res.scalars().all()

    # If user has no subscriptions in DB yet, scan their transactions or seed defaults
    if not subs:
        tx_res = await db.execute(
            select(Transaction).filter(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == "debit",
                Transaction.is_deleted == False
            )
        )
        tx_list = [
            {
                "description": t.description,
                "amount": float(t.amount),
                "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None,
                "transaction_type": "debit"
            }
            for t in tx_res.scalars().all()
        ]
        detected = subscription_tracker.detect_subscriptions(tx_list)

        for item in detected:
            sub_obj = Subscription(
                user_id=current_user.id,
                service_name=item["service_name"],
                amount=Decimal(str(item["amount"])),
                currency=item.get("currency", "INR"),
                billing_cycle=item.get("billing_cycle", "monthly"),
                recurring_type=item.get("recurring_type", "monthly_subscription"),
                confidence=Decimal(str(item.get("confidence", 0.90))),
                status=item.get("status", "confirmed"),
                last_paid_date=date.fromisoformat(item["last_paid_date"]) if item.get("last_paid_date") else None,
                next_billing_date=date.fromisoformat(item["next_billing_date"]),
                is_active=item.get("is_active", True)
            )
            db.add(sub_obj)
        await db.commit()

        # Re-fetch
        res_new = await db.execute(
            select(Subscription)
            .options(selectinload(Subscription.category))
            .filter(Subscription.user_id == current_user.id, Subscription.is_deleted == False)
            .order_by(Subscription.next_billing_date.asc())
        )
        subs = res_new.scalars().all()

    dtos = [_to_subscription_dto(s) for s in subs]
    active_subs = [s for s in dtos if s.is_active and s.status != "dismissed"]
    pending_subs = [s for s in dtos if s.status == "detected"]

    # Calculate Total Monthly and Annualized costs
    total_monthly = 0.0
    total_annual = 0.0
    by_type: Dict[str, float] = {
        "monthly_subscription": 0.0,
        "annual_subscription": 0.0,
        "recurring_bill": 0.0,
        "recurring_membership": 0.0
    }

    for s in active_subs:
        ann = s.annualized_cost
        mon = ann / 12.0
        total_monthly += mon
        total_annual += ann
        r_type = s.recurring_type
        if r_type not in by_type:
            by_type[r_type] = 0.0
        by_type[r_type] = round(by_type[r_type] + mon, 2)

    return SubscriptionDashboardResponse(
        total_monthly_recurring=round(total_monthly, 2),
        total_annual_recurring=round(total_annual, 2),
        active_subscriptions_count=len(active_subs),
        pending_detection_count=len(pending_subs),
        subscriptions_by_type=by_type,
        subscriptions=dtos
    )

@router.post("/scan", response_model=SubscriptionDashboardResponse)
async def scan_and_detect_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Scans the user's latest transaction history, detects recurring services,
    and updates the active subscription registry.
    """
    tx_res = await db.execute(
        select(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "debit",
            Transaction.is_deleted == False
        )
    )
    tx_list = [
        {
            "description": t.description,
            "amount": float(t.amount),
            "transaction_date": t.transaction_date.isoformat() if t.transaction_date else None,
            "transaction_type": "debit"
        }
        for t in tx_res.scalars().all()
    ]
    detected = subscription_tracker.detect_subscriptions(tx_list)

    # Check existing subscriptions
    existing_res = await db.execute(
        select(Subscription).filter(Subscription.user_id == current_user.id, Subscription.is_deleted == False)
    )
    existing_map = {s.service_name.lower(): s for s in existing_res.scalars().all()}

    for item in detected:
        s_name_lower = item["service_name"].lower()
        if s_name_lower in existing_map:
            # Update existing
            existing_sub = existing_map[s_name_lower]
            existing_sub.amount = Decimal(str(item["amount"]))
            existing_sub.confidence = Decimal(str(item["confidence"]))
            db.add(existing_sub)
        else:
            # Insert new detected subscription
            new_sub = Subscription(
                user_id=current_user.id,
                service_name=item["service_name"],
                amount=Decimal(str(item["amount"])),
                currency=item.get("currency", "INR"),
                billing_cycle=item.get("billing_cycle", "monthly"),
                recurring_type=item.get("recurring_type", "monthly_subscription"),
                confidence=Decimal(str(item.get("confidence", 0.90))),
                status=item.get("status", "detected"),
                last_paid_date=date.fromisoformat(item["last_paid_date"]) if item.get("last_paid_date") else None,
                next_billing_date=date.fromisoformat(item["next_billing_date"]),
                is_active=item.get("is_active", True)
            )
            db.add(new_sub)

    await db.commit()
    return await get_subscriptions_dashboard(current_user=current_user, db=db)

@router.post("/", response_model=SubscriptionOut)
async def create_subscription(
    sub_in: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    next_date = sub_in.next_billing_date or (date.today() + timedelta(days=30))
    sub = Subscription(
        user_id=current_user.id,
        service_name=sub_in.service_name,
        amount=Decimal(str(sub_in.amount)),
        currency="INR",
        billing_cycle=sub_in.billing_cycle or "monthly",
        recurring_type=sub_in.recurring_type or "monthly_subscription",
        confidence=Decimal("1.00"),
        status="confirmed",
        next_billing_date=next_date,
        is_active=True,
        category_id=sub_in.category_id
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return _to_subscription_dto(sub)

@router.post("/{sub_id}/confirm", response_model=SubscriptionOut)
async def confirm_subscription(
    sub_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Subscription).filter(Subscription.id == sub_id, Subscription.user_id == current_user.id)
    )
    sub = res.scalars().first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    sub.status = "confirmed"
    sub.is_active = True
    await db.commit()
    await db.refresh(sub)
    return _to_subscription_dto(sub)

@router.post("/{sub_id}/dismiss", response_model=SubscriptionOut)
async def dismiss_subscription(
    sub_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Subscription).filter(Subscription.id == sub_id, Subscription.user_id == current_user.id)
    )
    sub = res.scalars().first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    sub.status = "dismissed"
    sub.is_active = False
    await db.commit()
    await db.refresh(sub)
    return _to_subscription_dto(sub)

@router.put("/{sub_id}", response_model=SubscriptionOut)
async def update_subscription(
    sub_id: str,
    sub_update: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Subscription).filter(Subscription.id == sub_id, Subscription.user_id == current_user.id)
    )
    sub = res.scalars().first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    if sub_update.service_name is not None:
        sub.service_name = sub_update.service_name
    if sub_update.amount is not None:
        sub.amount = Decimal(str(sub_update.amount))
    if sub_update.billing_cycle is not None:
        sub.billing_cycle = sub_update.billing_cycle
    if sub_update.recurring_type is not None:
        sub.recurring_type = sub_update.recurring_type
    if sub_update.next_billing_date is not None:
        sub.next_billing_date = sub_update.next_billing_date
    if sub_update.status is not None:
        sub.status = sub_update.status
    if sub_update.is_active is not None:
        sub.is_active = sub_update.is_active

    await db.commit()
    await db.refresh(sub)
    return _to_subscription_dto(sub)

@router.delete("/{sub_id}")
async def delete_subscription(
    sub_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(Subscription).filter(Subscription.id == sub_id, Subscription.user_id == current_user.id)
    )
    sub = res.scalars().first()
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    await db.delete(sub)
    await db.commit()
    return {"message": "Subscription deleted successfully"}
