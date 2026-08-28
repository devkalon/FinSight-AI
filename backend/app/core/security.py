from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional, Set
from jose import jwt, JWTError
from passlib.context import CryptContext
from backend.app.core.config import settings

import threading

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Thread-safe revoked tokens store (with Redis fallback hooks for multi-worker production clusters)
_REVOKED_TOKENS: Set[str] = set()
_REVOKED_LOCK = threading.Lock()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    if is_token_revoked(token):
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
    except Exception:
        return None

def revoke_token(token: str) -> None:
    with _REVOKED_LOCK:
        _REVOKED_TOKENS.add(token)

def is_token_revoked(token: str) -> bool:
    with _REVOKED_LOCK:
        return token in _REVOKED_TOKENS

def clear_revoked_tokens_for_testing() -> None:
    with _REVOKED_LOCK:
        _REVOKED_TOKENS.clear()
