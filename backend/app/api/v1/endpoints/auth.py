from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    UserRegister, UserLogin, Token, UserProfile, UserUpdate, UserPreferences, LogoutResponse, PrivacyDeletionResponse
)
from backend.app.services.auth_service import auth_service
from backend.app.api.deps import get_current_user, oauth2_scheme

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    return await auth_service.register_user(db, user_in)

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await auth_service.authenticate_user(db, login_data)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.logout_user(db, token, current_user)

@router.get("/me", response_model=UserProfile)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserProfile)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.update_user_profile(db, current_user, user_update)

@router.put("/me/preferences", response_model=UserProfile)
async def update_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await auth_service.update_user_preferences(db, current_user, preferences)

@router.delete("/me", response_model=PrivacyDeletionResponse)
async def delete_account_and_data(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Privacy & Right-to-be-Forgotten:
    Permanently deletes user profile, transactions, budgets, goals, documents, and credentials.
    """
    return await auth_service.delete_user_data(db, token, current_user)
