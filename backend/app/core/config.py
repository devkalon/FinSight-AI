import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinSight AI — Personal Finance & Wealth Management Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    # Dev-only fallback. Production MUST provide SECRET_KEY via environment;
    # validate_security() below rejects this and other insecure/known values in production.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-only-insecure-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./finsight.db")

    # CORS (Strict whitelist without wildcard origins when allow_credentials=True)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    # Storage for uploaded files
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

    # LLM Settings (Optional API keys with graceful offline / built-in fallbacks)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Google OAuth 2.0 Credentials
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback/google")

    class Config:
        case_sensitive = True
        env_file = ".env"

    def validate_security(self):
        if self.ENVIRONMENT.lower() != "production":
            return

        # Values that must never be used in production: dev defaults, obviously
        # insecure markers, and any secret that was ever committed to source control.
        insecure_markers = ("super-secret", "default", "dev-only", "change-me", "changeme")
        known_committed_keys = {
            # Previously hardcoded as the docker-compose SECRET_KEY fallback.
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }

        key = self.SECRET_KEY or ""
        if (
            not key
            or len(key) < 32
            or any(marker in key.lower() for marker in insecure_markers)
            or key in known_committed_keys
        ):
            raise ValueError(
                "CRITICAL SECURITY ERROR: Production deployment requires a secure, "
                "custom SECRET_KEY (>=32 chars, not a dev default or previously "
                "committed value) set in environment variables."
            )

settings = Settings()
settings.validate_security()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "receipts"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "statements"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "books"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "reports"), exist_ok=True)
