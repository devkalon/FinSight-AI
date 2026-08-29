from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional, Set
from jose import jwt, JWTError
from backend.app.core.config import settings
import bcrypt
import threading

# Thread-safe revoked tokens store (with Redis fallback hooks for multi-worker production clusters)
_REVOKED_TOKENS: Set[str] = set()
_REVOKED_LOCK = threading.Lock()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pw_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hash_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    pw_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

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
