"""Javni endpointi bez auth — za Next.js SSR/SSG."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BlogPost, Job
import bleach


router = APIRouter()

@router.get("/jobs/search")
def search_jobs(
    work_mode: str | None = None, seniority: str | None = None, category: str | None = None,
    country: str | None = None, city: str | None = None, employment_type: str | None = None,
    salary_min: float | None = None, salary_max: float | None = None, posted_within: int | None = Query(None, ge=1, le=3650),
    visa_only: bool = False, housing_only: bool = False, relocation_only: bool = False,
    language: str | None = None, source: str | None = None, query: str | None = None,
    sort: str = Query("newest", pattern="^(match_score|newest|salary|relevance)$"),
    limit: int = Query(30, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db),
):
    q = db.query(Job).filter(Job.is_active.is_(True))
    for column, value in ((Job.work_mode, work_mode), (Job.seniority, seniority), (Job.category, category), (Job.city, city), (Job.employment_type, employment_type), (Job.language, language), (Job.source, source)):
        if value: q = q.filter(func.lower(column) == value.lower())
    if country: q = q.filter(Job.country_code == country.upper())
    if salary_min is not None: q = q.filter(Job.salary_max >= salary_min)
    if salary_max is not None: q = q.filter(Job.salary_min <= salary_max)
    if visa_only: q = q.filter(Job.visa_sponsorship.is_(True))
    if housing_only: q = q.filter(Job.housing_provided.is_(True))
    if relocation_only: q = q.filter(Job.relocation_support.is_(True))
    if posted_within: q = q.filter(Job.posted_at >= datetime.now(timezone.utc) - timedelta(days=posted_within))
    if query:
        term = f"%{query.strip()}%"
        q = q.filter(Job.title.ilike(term) | Job.company.ilike(term) | Job.description.ilike(term))
    total = q.count()
    if sort == "salary": q = q.order_by(desc(Job.salary_max), desc(Job.scraped_at))
    else: q = q.order_by(desc(Job.posted_at if sort == "newest" else Job.scraped_at))
    jobs = q.offset(offset).limit(limit).all()
    facet_base = db.query(Job).filter(Job.is_active.is_(True))
    facets = {"category": [{"value": x[0], "count": x[1]} for x in facet_base.with_entities(Job.category, func.count(Job.id)).filter(Job.category.isnot(None)).group_by(Job.category).order_by(desc(func.count(Job.id))).all()], "country": [{"value": x[0], "count": x[1]} for x in facet_base.with_entities(Job.country_code, func.count(Job.id)).filter(Job.country_code.isnot(None)).group_by(Job.country_code).order_by(desc(func.count(Job.id))).all()]}
    return {"total": total, "items": [_job_to_dict(j) for j in jobs], "facets": facets, "next_offset": offset + len(jobs) if offset + len(jobs) < total else None}


def _job_to_dict(j: Job) -> dict:
    return {
        "id": str(j.id),
        "slug": j.slug,
        "title": j.title,
        "company": j.company,
        "company_logo": j.company_logo,
        "location": j.location,
        "city": j.city,
        "country_code": j.country_code,
        "work_mode": j.work_mode,
        "category": j.category,
        "seniority": j.seniority,
        "language": j.language,
        "allowed_countries": j.allowed_countries,
        "visa_sponsorship": j.visa_sponsorship,
        "housing_provided": j.housing_provided,
        "relocation_support": j.relocation_support,
        "salary_min": float(j.salary_min) if j.salary_min else None,
        "salary_max": float(j.salary_max) if j.salary_max else None,
        "currency": j.currency,
        "salary_period": j.salary_period,
        "description": bleach.clean(j.description or "", tags=["p", "br", "strong", "em", "ul", "ol", "li", "h2", "h3"], attributes={}, strip=True),
        "url": j.url,
        "seo_title": j.seo_title,
        "seo_description": j.seo_description,
        "keywords": j.keywords,
        "posted_at": j.posted_at.isoformat() if j.posted_at else None,
        "expires_at": j.expires_at.isoformat() if j.expires_at else None,
        "updated_at": j.scraped_at.isoformat() if j.scraped_at else None,
    }


@router.get("/jobs/latest")
def jobs_latest(limit: int = 12, db: Session = Depends(get_db)):
    jobs = (
        db.query(Job)
        .filter(Job.is_active.is_(True))
        .order_by(desc(Job.scraped_at))
        .limit(limit)
        .all()
    )
    return {"items": [_job_to_dict(j) for j in jobs]}


@router.get("/jobs/by-filter")
def jobs_by_filter(
    work_mode: str | None = None,
    category: str | None = None,
    country: str | None = None,
    city: str | None = None,
    q: str | None = None,
    limit: int = 12,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Job).filter(Job.is_active.is_(True))
    if work_mode:
        query = query.filter(Job.work_mode == work_mode)
    if category:
        query = query.filter(Job.category == category)
    if country:
        query = query.filter(Job.country_code == country.upper())
    if city:
        query = query.filter(func.lower(Job.city) == city.lower())
    if q:
        like = f"%{q}%"
        query = query.filter(Job.title.ilike(like) | Job.company.ilike(like))

    total = query.count()
    jobs = query.order_by(desc(Job.scraped_at)).limit(limit).offset(offset).all()
    return {"total": total, "items": [_job_to_dict(j) for j in jobs]}


@router.get("/jobs/by-country")
def jobs_by_country(country: str, limit: int = 12, db: Session = Depends(get_db)):
    jobs = (
        db.query(Job)
        .filter(Job.is_active.is_(True), Job.country_code == country.upper())
        .order_by(desc(Job.scraped_at))
        .limit(limit)
        .all()
    )
    return {"items": [_job_to_dict(j) for j in jobs]}


@router.get("/jobs/{slug}")
def job_by_slug(slug: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter_by(slug=slug).first()
    if not job:
        raise HTTPException(404, "Job not found")
    job.views = (job.views or 0) + 1
    db.commit()
    return _job_to_dict(job)


@router.get("/jobs/by-id/{job_id}")
def job_by_id(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404)
    return _job_to_dict(job)


@router.get("/jobs/sitemap")
def jobs_sitemap(limit: int = 5000, db: Session = Depends(get_db)):
    jobs = (
        db.query(Job)
        .filter(Job.is_active.is_(True))
        .order_by(desc(Job.scraped_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "slug": j.slug,
            "updated_at": j.scraped_at.isoformat() if j.scraped_at else None,
        }
        for j in jobs
    ]


@router.get("/cities")
def cities(db: Session = Depends(get_db)):
    rows = (
        db.query(Job.city, func.count(Job.id).label("n"))
        .filter(Job.is_active.is_(True), Job.city.isnot(None))
        .group_by(Job.city)
        .order_by(desc("n"))
        .limit(50)
        .all()
    )
    return [{"city": r.city, "count": r.n} for r in rows]


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    rows = (
        db.query(Job.category, func.count(Job.id).label("n"))
        .filter(Job.is_active.is_(True), Job.category.isnot(None))
        .group_by(Job.category)
        .order_by(desc("n"))
        .all()
    )
    return [{"category": r.category, "count": r.n} for r in rows]


@router.get("/countries")
def countries(db: Session = Depends(get_db)):
    rows = (
        db.query(Job.country_code, func.count(Job.id).label("n"))
        .filter(Job.is_active.is_(True), Job.country_code.isnot(None))
        .group_by(Job.country_code)
        .order_by(desc("n"))
        .all()
    )
    return [{"country": r.country_code, "count": r.n} for r in rows]


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Job.id)).filter(Job.is_active.is_(True)).scalar()
    remote = db.query(func.count(Job.id)).filter(Job.is_active.is_(True), Job.work_mode == "remote").scalar()
    with_visa = db.query(func.count(Job.id)).filter(Job.is_active.is_(True), Job.visa_sponsorship.is_(True)).scalar()
    with_housing = db.query(func.count(Job.id)).filter(Job.is_active.is_(True), Job.housing_provided.is_(True)).scalar()
    return {
        "total_jobs": total,
        "remote_jobs": remote,
        "visa_sponsorship_jobs": with_visa,
        "housing_provided_jobs": with_housing,
    }
