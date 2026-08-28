import logging
import time
import uuid
from typing import Dict
from contextlib import asynccontextmanager
from collections import defaultdict
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.api.v1.api_router import api_router

logger = logging.getLogger("finsight.security")

# Rate Limiter State (IP -> window timestamps)
_RATE_LIMIT_STORE: Dict[str, list] = defaultdict(list)

def clear_rate_limit_store():
    _RATE_LIMIT_STORE.clear()
RATE_LIMIT_RULES = {
    "/auth/login": (15, 60),      # 15 requests per 60s
    "/auth/register": (10, 60),   # 10 requests per 60s
    "/upload": (30, 60),          # 30 requests per 60s
    "/advisor/chat": (60, 60),    # 60 requests per 60s
    "default": (300, 60)          # 300 requests per 60s
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    await init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# SEC-08: Security Headers Middleware
@app.middleware("http")
async def add_security_headers_middleware(request: Request, call_next):
    # SEC-03: Simple IP Rate Limiting Check
    client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "127.0.0.1")
    path = request.url.path
    
    # Determine rule limit and window
    limit, window = RATE_LIMIT_RULES["default"]
    for prefix, rule in RATE_LIMIT_RULES.items():
        if prefix != "default" and prefix in path:
            limit, window = rule
            break

    now = time.time()
    timestamps = [ts for ts in _RATE_LIMIT_STORE[client_ip] if now - ts < window]
    _RATE_LIMIT_STORE[client_ip] = timestamps

    if len(timestamps) >= limit:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Rate limit exceeded. Please slow down your requests.", "retry_after_seconds": window}
        )
    
    _RATE_LIMIT_STORE[client_ip].append(now)

    response: Response = await call_next(request)
    
    # Add Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:;"
    return response

# SEC-02: Set clean CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

# SEC-07: Global Exception Handler for Sanitized 500 Responses
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = uuid.uuid4().hex[:8]
    logger.error(f"Unhandled Exception [ID: {error_id}] on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Our security monitoring team has been notified.",
            "error_id": error_id
        }
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "FinSight AI API Gateway",
        "version": "1.0.0",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
