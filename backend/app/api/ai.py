from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.ai.cover_letter import generate_cover_letter
from app.ai.cv_parser import parse_cv_text, parse_date
from app.ai.embedder import embed_profile
from app.api.deps import current_user
from app.database import get_db
from app.models import Experience, Job, Profile, Skill, User


router = APIRouter()


def _extract_text(filename: str, data: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = PdfReader(BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if lower.endswith(".txt") or lower.endswith(".md"):
        return data.decode("utf-8", errors="ignore")
    if lower.endswith(".docx"):
        from docx import Document
        doc = Document(BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    raise HTTPException(400, "Nepodržan format. Koristi PDF, DOCX, TXT ili MD.")


@router.post("/import-cv")
async def import_cv(
    file: UploadFile = File(...),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    """Upload CV-a → AI parsira → popuni profil i vault."""
    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(413, "CV je prevelik. Maksimalna veličina je 10 MB.")
    text = _extract_text(file.filename or "", raw)
    if len(text.strip()) < 50:
        raise HTTPException(400, "CV izgleda prazan ili nečitljiv.")

    parsed = parse_cv_text(text)
    profile = db.query(Profile).filter_by(user_id=user.id).first()

    profile.title = parsed.get("primary_role") or profile.title
    profile.timezone = parsed.get("preferred_timezone") or profile.timezone
    profile.summary = parsed.get("summary") or profile.summary
    profile.seniority = parsed.get("seniority") or profile.seniority
    profile.languages = parsed.get("languages") or profile.languages

    # Reset iskustva i vještina
    for e in list(profile.experiences):
        db.delete(e)
    for s in list(profile.skills):
        db.delete(s)
    db.flush()

    for exp in parsed.get("experiences", []):
        profile.experiences.append(Experience(
            company=exp.get("company") or "",
            role=exp.get("role") or "",
            start_date=parse_date(exp.get("start")),
            end_date=parse_date(exp.get("end")),
            description=exp.get("description"),
            technologies=exp.get("technologies") or [],
        ))

    for sk in parsed.get("skills", []):
        profile.skills.append(Skill(
            name=sk.get("name") or "",
            category=sk.get("category"),
            level=sk.get("level"),
            years=sk.get("years"),
        ))

    db.flush()
    embed_profile(profile)
    db.commit()

    return {
        "ok": True,
        "detected_language": parsed.get("_detected_language"),
        "primary_role": profile.title,
        "seniority": profile.seniority,
        "skills_count": len(profile.skills),
        "experiences_count": len(profile.experiences),
    }


@router.post("/cover-letter/{job_id}")
def cover_letter(
    job_id: str,
    language: str = "bs",
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    profile = db.query(Profile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    letter = generate_cover_letter(profile, job, language=language)
    return {"cover_letter": letter, "language": language}
