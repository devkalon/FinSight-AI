from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from backend.app.core.security import verify_password, get_password_hash, create_access_token, revoke_token
from backend.app.models.user import User, Profile
from backend.app.models.category import Category
from backend.app.models.audit_log import AuditLog
from backend.app.schemas.auth import (
    UserRegister, UserLogin, Token, UserUpdate, UserPreferences, LogoutResponse, PrivacyDeletionResponse
)
from backend.app.repositories.user_repo import user_repository

DEFAULT_CATEGORIES = [
    {"name": "Food & Dining", "group_type": "Want", "icon": "Utensils", "color": "#F59E0B"},
    {"name": "Groceries", "group_type": "Need", "icon": "ShoppingCart", "color": "#10B981"},
    {"name": "Transportation", "group_type": "Need", "icon": "Car", "color": "#3B82F6"},
    {"name": "Entertainment", "group_type": "Want", "icon": "Film", "color": "#EC4899"},
    {"name": "Shopping", "group_type": "Want", "icon": "ShoppingBag", "color": "#8B5CF6"},
    {"name": "Utilities & Bills", "group_type": "Need", "icon": "Zap", "color": "#EF4444"},
    {"name": "Healthcare & Fitness", "group_type": "Need", "icon": "HeartPulse", "color": "#14B8A6"},
    {"name": "Investment & Savings", "group_type": "Savings", "icon": "TrendingUp", "color": "#059669"},
    {"name": "Income", "group_type": "Income", "icon": "Wallet", "color": "#22C55E"}
]

class AuthService:
    async def register_user(self, db: AsyncSession, user_in: UserRegister) -> Token:
        existing = await user_repository.get_by_email(db, user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists."
            )

        new_user = User(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            is_active=True,
            is_verified=False
        )
        db.add(new_user)
        await db.flush()

        # Create Profile
        profile = Profile(
            user_id=new_user.id,
            full_name=user_in.full_name,
            preferred_currency=user_in.preferred_currency or "INR",
            preferred_guru=user_in.preferred_guru or "balanced",
            monthly_income=Decimal(str(user_in.monthly_income or 0.00)),
            country_code="IN"
        )
        db.add(profile)

        # Seed initial categories
        for cat in DEFAULT_CATEGORIES:
            category = Category(
                user_id=new_user.id,
                name=cat["name"],
                group_type=cat["group_type"],
                icon=cat["icon"],
                color=cat["color"],
                is_custom=False
            )
            db.add(category)

        # Audit Log
        audit = AuditLog(
            user_id=new_user.id,
            action="user_registered",
            entity_type="User",
            entity_id=new_user.id,
            details={"email": new_user.email}
        )
        db.add(audit)

        await db.commit()
        await db.refresh(new_user)

        token = create_access_token(new_user.id)
        return Token(
            access_token=token,
            token_type="bearer",
            user_id=new_user.id,
            email=new_user.email,
            full_name=user_in.full_name
        )

    async def authenticate_user(self, db: AsyncSession, login_data: UserLogin) -> Token:
        res = await db.execute(
            select(User).options(selectinload(User.profile)).filter(User.email == login_data.email)
        )
        user = res.scalars().first()
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account has been deactivated or deleted",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # Record Login Audit Log
        audit = AuditLog(
            user_id=user.id,
            action="user_login",
            entity_type="User",
            entity_id=user.id,
            details={"email": user.email}
        )
        db.add(audit)
        await db.commit()

        token = create_access_token(user.id)
        full_name = user.profile.full_name if user.profile else user.email.split("@")[0]
        return Token(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            full_name=full_name
        )

    async def logout_user(self, db: AsyncSession, token: str, user: User) -> LogoutResponse:
        revoke_token(token)
        audit = AuditLog(
            user_id=user.id,
            action="user_logout",
            entity_type="User",
            entity_id=user.id
        )
        db.add(audit)
        await db.commit()
        return LogoutResponse()

    async def update_user_profile(self, db: AsyncSession, user: User, user_update: UserUpdate) -> User:
        res = await db.execute(select(Profile).filter(Profile.user_id == user.id))
        profile = res.scalars().first()
        if not profile:
            profile = Profile(user_id=user.id, full_name=user.email.split("@")[0])
            db.add(profile)

        if user_update.full_name is not None:
            profile.full_name = user_update.full_name
        if user_update.preferred_currency is not None:
            profile.preferred_currency = user_update.preferred_currency
        if user_update.preferred_guru is not None:
            profile.preferred_guru = user_update.preferred_guru
        if user_update.monthly_income is not None:
            profile.monthly_income = Decimal(str(user_update.monthly_income))
        if user_update.risk_tolerance is not None:
            profile.risk_tolerance = user_update.risk_tolerance
        if user_update.tax_regime is not None:
            profile.tax_regime = user_update.tax_regime

        await db.commit()
        await db.refresh(user)
        return user

    async def update_user_preferences(self, db: AsyncSession, user: User, prefs: UserPreferences) -> User:
        res = await db.execute(select(Profile).filter(Profile.user_id == user.id))
        profile = res.scalars().first()
        if not profile:
            profile = Profile(user_id=user.id, full_name=user.email.split("@")[0])
            db.add(profile)

        if prefs.preferred_currency is not None:
            profile.preferred_currency = prefs.preferred_currency
        if prefs.preferred_guru is not None:
            profile.preferred_guru = prefs.preferred_guru
        if prefs.risk_tolerance is not None:
            profile.risk_tolerance = prefs.risk_tolerance
        if prefs.tax_regime is not None:
            profile.tax_regime = prefs.tax_regime

        await db.commit()
        await db.refresh(user)
        return user

    async def delete_user_data(self, db: AsyncSession, token: str, user: User) -> PrivacyDeletionResponse:
        # Soft delete & anonymize user data (GDPR / Privacy compliance)
        user_id = user.id
        revoke_token(token)

        audit = AuditLog(
            user_id=user_id,
            action="user_data_deleted_gdpr",
            entity_type="User",
            entity_id=user_id,
            details={"status": "permanently_deleted"}
        )
        db.add(audit)

        # SEC-05: Remove physical files from disk before database deletion (GDPR compliance)
        from backend.app.models.document import FinancialDocument
        doc_res = await db.execute(select(FinancialDocument).filter(FinancialDocument.user_id == user_id))
        docs = doc_res.scalars().all()
        for doc in docs:
            if doc.storage_path and os.path.exists(doc.storage_path):
                try:
                    os.remove(doc.storage_path)
                except Exception:
                    pass

        # Remove user cascades
        await db.delete(user)
        await db.commit()

        return PrivacyDeletionResponse(
            message="All personal financial data, documents, and credentials have been permanently deleted.",
            deleted_user_id=user_id,
            timestamp=datetime.now(timezone.utc)
        )

auth_service = AuthService()
