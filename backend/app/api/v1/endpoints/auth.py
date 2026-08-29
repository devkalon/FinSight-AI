from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.auth import (
    UserRegister, UserLogin, GoogleOAuthRequest, GoogleAuthUrlResponse, GoogleCallbackRequest, Token, UserProfile, UserUpdate, UserPreferences, LogoutResponse, PrivacyDeletionResponse
)
from backend.app.services.auth_service import auth_service
from backend.app.api.deps import get_current_user, oauth2_scheme
from backend.app.core.config import settings
import logging
import httpx

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    return await auth_service.register_user(db, user_in)

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await auth_service.authenticate_user(db, login_data)

@router.get("/google/url", response_model=GoogleAuthUrlResponse)
async def get_google_auth_url():
    client_id = settings.GOOGLE_CLIENT_ID
    if not client_id:
        return GoogleAuthUrlResponse(
            url="https://accounts.google.com/o/oauth2/v2/auth",
            client_id_configured=False
        )
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return GoogleAuthUrlResponse(url=url, client_id_configured=True)

@router.post("/google/callback", response_model=Token)
async def google_callback(cb: GoogleCallbackRequest, db: AsyncSession = Depends(get_db)):
    # If real Google credentials are configured, the exchange MUST succeed on its
    # own terms. We never silently fall back to a shared mock account on failure,
    # since that would both mask real errors and be a security hole.
    if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
        try:
            async with httpx.AsyncClient() as client:
                token_resp = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": cb.code,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                        "grant_type": "authorization_code",
                    },
                    timeout=10.0
                )
        except httpx.HTTPError as exc:
            logger.exception("Google token endpoint request failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not reach Google to complete sign-in. Please try again."
            ) from exc

        if token_resp.status_code != 200:
            logger.error(
                "Google token exchange failed: status=%s body=%s",
                token_resp.status_code, token_resp.text
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google authorization code could not be exchanged."
            )

        access_token = token_resp.json().get("access_token")

        try:
            async with httpx.AsyncClient() as client:
                user_info_resp = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )
        except httpx.HTTPError as exc:
            logger.exception("Google userinfo request failed")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not retrieve your Google profile. Please try again."
            ) from exc

        if user_info_resp.status_code != 200:
            logger.error(
                "Google userinfo failed: status=%s body=%s",
                user_info_resp.status_code, user_info_resp.text
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not verify your Google identity."
            )

        info = user_info_resp.json()
        return await auth_service.authenticate_google_user(
            db,
            GoogleOAuthRequest(
                email=info.get("email"),
                full_name=info.get("name"),
                avatar_url=info.get("picture"),
                google_id=info.get("sub")
            )
        )

    # No Google credentials configured. The mock user is a development-only
    # convenience and must never be reachable in production.
    if settings.ENVIRONMENT.lower() == "production":
        logger.error("Google OAuth is not configured but a callback was received in production.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured on this server."
        )

    logger.warning("GOOGLE_CLIENT_ID/SECRET not set — using development mock Google user.")
    return await auth_service.authenticate_google_user(
        db,
        GoogleOAuthRequest(email="google.user@finsight.ai", full_name="Google Workspace User")
    )

@router.post("/google", response_model=Token)
async def google_oauth_login(google_in: GoogleOAuthRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.authenticate_google_user(db, google_in)

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
