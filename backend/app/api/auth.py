from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from app.api.deps import hash_password, verify_password
from app.config import settings
from app.database import get_db
from app.models import Profile, ProfileVault, User

router = APIRouter()
class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=200)

def token_for(user: User) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_MINUTES)
    return jwt.encode({"sub": str(user.id), "exp": exp}, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

@router.post("/register")
def register(data: Credentials, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=data.email.lower()).first(): raise HTTPException(409, "Email already registered")
    user = User(email=data.email.lower(), password_hash=hash_password(data.password), full_name=data.full_name)
    user.profile = Profile(); user.vault = ProfileVault(email=data.email.lower())
    db.add(user); db.commit(); db.refresh(user)
    return {"token": token_for(user), "user": {"email": user.email, "full_name": user.full_name}}

@router.post("/login")
def login(data: Credentials, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash): raise HTTPException(401, "Invalid credentials")
    return {"token": token_for(user), "user": {"email": user.email, "full_name": user.full_name}}
