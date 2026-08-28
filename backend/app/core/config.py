import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinSight AI — Personal Finance & Wealth Management Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-finsight-ai-jwt-key-2026-secure-token-vault")
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

    class Config:
        case_sensitive = True
        env_file = ".env"

    def validate_security(self):
        if self.ENVIRONMENT.lower() == "production" and (
            not self.SECRET_KEY or "super-secret" in self.SECRET_KEY or "default" in self.SECRET_KEY
        ):
            raise ValueError("CRITICAL SECURITY ERROR: Production deployment requires a secure, custom SECRET_KEY set in environment variables.")

settings = Settings()
settings.validate_security()

# Ensure uploads directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "receipts"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "statements"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "books"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "reports"), exist_ok=True)
