from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer(auto_error=False)

def hash_password(value: str) -> str: return pwd_context.hash(value)
def verify_password(value: str, hashed: str) -> bool: return pwd_context.verify(value, hashed)
def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if not credentials: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try: payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]); user_id = payload.get("sub")
    except JWTError: raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, user_id) if user_id else None
    if not user: raise HTTPException(status_code=401, detail="Invalid token")
    return user
