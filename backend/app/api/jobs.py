from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.database import get_db
from app.eligibility.rules import can_apply
from app.models import Job, Profile, User
from app.services.matching import hybrid_match


router = APIRouter()


@router.get("/feed")
def feed(
    limit: int = 30,
    only_eligible: bool = True,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter_by(user_id=user.id).first()
    if not profile or profile.embedding is None:
        return {"items": [], "reason": "profile_not_ready"}

    matches = hybrid_match(db, profile, limit=limit * 3)
    items = []
    for m in matches:
        job = m["job"]
        elig = can_apply(job, profile)
        if only_eligible and not elig["eligible"]:
            continue
        score = round(m["final_score"] * 100 * (1 - elig["score_penalty"]), 1)
        items.append({
            "id": str(job.id),
            "slug": job.slug,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "city": job.city,
            "work_mode": job.work_mode,
            "category": job.category,
            "seniority": job.seniority,
            "allowed_countries": job.allowed_countries,
            "visa_sponsorship": job.visa_sponsorship,
            "housing_provided": job.housing_provided,
            "salary_min": float(job.salary_min) if job.salary_min else None,
            "salary_max": float(job.salary_max) if job.salary_max else None,
            "currency": job.currency,
            "url": job.url,
            "score_pct": score,
            "vector_score": round(m["vector_score"] * 100, 1),
            "keyword_score": round(m["keyword_score"] * 100, 1),
            "eligibility": elig,
        })
    items.sort(key=lambda x: x["score_pct"], reverse=True)
    return {"items": items[:limit]}


@router.get("/{job_id}")
def get_job(job_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return {
        "id": str(job.id),
        "slug": job.slug,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "work_mode": job.work_mode,
        "description": job.description,
        "salary_min": float(job.salary_min) if job.salary_min else None,
        "salary_max": float(job.salary_max) if job.salary_max else None,
        "currency": job.currency,
        "url": job.url,
        "posted_at": job.posted_at.isoformat() if job.posted_at else None,
    }
