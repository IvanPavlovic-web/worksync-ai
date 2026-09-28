from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import base64
import hashlib
import hmac
import secrets
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

bearer = HTTPBearer(auto_error=False)

def hash_password(value: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(value.encode(), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$" + base64.urlsafe_b64encode(salt + digest).decode()

def verify_password(value: str, hashed: str) -> bool:
    try:
        raw = base64.urlsafe_b64decode(hashed.removeprefix("scrypt$").encode())
        salt, expected = raw[:16], raw[16:]
        actual = hashlib.scrypt(value.encode(), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False
def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try: payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]); user_id = payload.get("sub")
    except JWTError: raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, user_id) if user_id else None
    if not user: raise HTTPException(status_code=401, detail="Invalid token")
    return user
