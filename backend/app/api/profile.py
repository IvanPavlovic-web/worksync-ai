from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.database import get_db
from app.models import Profile, User

router = APIRouter()
@router.get("")
def get_profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    p = db.query(Profile).filter_by(user_id=user.id).first()
    return {"title": p.title, "summary": p.summary, "seniority": p.seniority, "languages": p.languages, "skills": [s.name for s in p.skills]} if p else {}
