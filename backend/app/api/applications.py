from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.autopilot.queue import enqueue_apply
from app.api.deps import current_user
from app.database import get_db
from app.models import Application, Job, User


router = APIRouter()
VALID_STATUSES = {"saved", "applied", "interview", "offer", "rejected", "prefill"}


class CreateIn(BaseModel):
    job_id: str
    status: str = "saved"
    match_score: float | None = None


class StatusIn(BaseModel):
    status: str


class BulkIn(BaseModel):
    job_ids: list[str]


@router.get("")
def list_apps(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(Application).filter_by(user_id=user.id).all()
    out = []
    for a in rows:
        job = db.get(Job, a.job_id)
        out.append({
            "id": str(a.id),
            "job_id": str(a.job_id),
            "status": a.status,
            "match_score": float(a.match_score) if a.match_score else None,
            "applied_at": a.applied_at.isoformat() if a.applied_at else None,
            "updated_at": a.updated_at.isoformat(),
            "job": {
                "title": job.title if job else "",
                "company": job.company if job else "",
                "url": job.url if job else "",
                "slug": job.slug if job else "",
            },
        })
    return out


@router.post("")
def create(data: CreateIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if data.status not in VALID_STATUSES:
        raise HTTPException(400, "Invalid status")
    exists = db.query(Application).filter_by(user_id=user.id, job_id=data.job_id).first()
    if exists:
        return {"id": str(exists.id), "status": exists.status}
    a = Application(
        user_id=user.id,
        job_id=data.job_id,
        status=data.status,
        match_score=data.match_score,
    )
    db.add(a)
    db.commit()
    return {"id": str(a.id), "status": a.status}


@router.patch("/{app_id}")
def update_status(
    app_id: str,
    data: StatusIn,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if data.status not in VALID_STATUSES:
        raise HTTPException(400, "Invalid status")
    a = db.query(Application).filter_by(id=app_id, user_id=user.id).first()
    if not a:
        raise HTTPException(404)
    a.status = data.status
    if data.status == "applied" and not a.applied_at:
        a.applied_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True, "status": a.status}


@router.delete("/{app_id}")
def delete_app(app_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    a = db.query(Application).filter_by(id=app_id, user_id=user.id).first()
    if not a:
        raise HTTPException(404)
    db.delete(a)
    db.commit()
    return {"ok": True}




@router.post("/auto-apply/{job_id}")
def auto_apply(job_id: str, user: User = Depends(current_user), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404)
    return enqueue_apply(str(user.id), job_id, job.source)


@router.post("/auto-apply-bulk")
def auto_apply_bulk(data: BulkIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    queued = 0
    rejected = 0
    for jid in data.job_ids:
        job = db.get(Job, jid)
        if not job:
            continue
        res = enqueue_apply(str(user.id), jid, job.source)
        if res.get("queued"):
            queued += 1
        else:
            rejected += 1
    return {"queued": queued, "rejected": rejected}
