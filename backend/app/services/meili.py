import meilisearch

from app.config import settings
from app.models import Job


def get_client() -> meilisearch.Client:
    return meilisearch.Client(settings.MEILI_URL, settings.MEILI_KEY)


INDEX_NAME = "jobs"


def ensure_index():
    client = get_client()
    try:
        client.create_index(INDEX_NAME, {"primaryKey": "id"})
    except Exception:
        pass
    idx = client.index(INDEX_NAME)
    idx.update_settings({
        "searchableAttributes": ["title", "company", "description", "city", "location"],
        "filterableAttributes": ["work_mode", "category", "seniority", "country_code", "language", "source"],
        "sortableAttributes": ["posted_at", "salary_max"],
        "rankingRules": ["words", "typo", "proximity", "attribute", "sort", "exactness"],
    })


def job_to_doc(job: Job) -> dict:
    return {
        "id": str(job.id),
        "title": job.title,
        "company": job.company or "",
        "description": (job.description or "")[:5000],
        "location": job.location or "",
        "city": job.city or "",
        "country_code": job.country_code or "",
        "work_mode": job.work_mode or "",
        "category": job.category or "",
        "seniority": job.seniority or "",
        "language": job.language or "",
        "source": job.source,
        "salary_min": float(job.salary_min) if job.salary_min else 0,
        "salary_max": float(job.salary_max) if job.salary_max else 0,
        "posted_at": int(job.posted_at.timestamp()) if job.posted_at else 0,
        "url": job.url,
    }


def sync_all_jobs_to_meili(db) -> dict:
    ensure_index()
    client = get_client()
    idx = client.index(INDEX_NAME)
    jobs = db.query(Job).filter(Job.is_active.is_(True)).all()
    docs = [job_to_doc(j) for j in jobs]
    if docs:
        idx.add_documents(docs)
    return {"synced": len(docs)}


def search(query: str, limit: int = 50, filters: str | None = None) -> dict:
    client = get_client()
    idx = client.index(INDEX_NAME)
    opts = {"limit": limit}
    if filters:
        opts["filter"] = filters
    return idx.search(query, opts)