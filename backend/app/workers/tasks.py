import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from rapidfuzz.fuzz import ratio

from slugify import slugify
from sqlalchemy.orm import Session

from app.ai.embedder import embed_job, embed_profile
from app.classifier.pipeline import enrich_job
from app.database import SessionLocal
from app.models import Application, Job, Profile, ProfileVault
from app.scrapers.registry import get_scrapers_for_tier
from app.services.meili import sync_all_jobs_to_meili
from app.workers.celery_app import celery


# ---------- HELPERS ----------

def _unique_slug(db: Session, title: str, company: str, reserved: set[str] | None = None) -> str:
    base = slugify(f"{title}-{company or 'job'}")[:80]
    slug = base
    i = 1
    reserved = reserved or set()
    while slug in reserved or db.query(Job).filter_by(slug=slug).first():
        slug = f"{base}-{i}"
        i += 1
    return slug


def _persist_jobs(db: Session, raws: list) -> int:
    added = 0
    reserved_slugs: set[str] = set()
    for raw in raws:
        if not raw.url:
            continue
        existing = db.query(Job).filter_by(url=raw.url).first()
        if existing:
            existing.source_ids = list(set((existing.source_ids or []) + [raw.external_id]))
            continue
        possible = db.query(Job).filter(Job.is_active.is_(True)).filter(Job.company == raw.company).all()
        duplicate = next((j for j in possible if ratio(f"{j.title} {j.company}", f"{raw.title} {raw.company}") >= 90), None)
        if duplicate:
            duplicate.source_ids = list(set((duplicate.source_ids or []) + [raw.external_id]))
            continue
        fields = enrich_job(raw)
        fields["slug"] = _unique_slug(db, raw.title, raw.company, reserved_slugs)
        reserved_slugs.add(fields["slug"])
        fields["source_ids"] = [raw.external_id]
        try:
            job = Job(**fields)
            db.add(job)
            added += 1
        except Exception as e:
            print(f"[persist] failed {raw.url}: {e}")
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return added


# ---------- SCRAPING ----------

@celery.task
def scrape_tier(tier: str = "critical"):
    db = SessionLocal()
    stats = {}
    try:
        for name, scraper, kwargs in get_scrapers_for_tier(tier):
            try:
                raws = scraper.fetch(**kwargs)
                added = _persist_jobs(db, raws)
                stats[name] = {"fetched": len(raws), "added": added}
            except Exception as e:
                db.rollback()
                stats[name] = f"ERROR: {e}"
    finally:
        db.close()
    return {"tier": tier, "stats": stats}


@celery.task
def scrape_source(name: str):
    from app.scrapers.registry import get_scraper
    scraper, kwargs = get_scraper(name)
    if not scraper:
        return {"error": f"unknown source {name}"}
    db = SessionLocal()
    try:
        raws = scraper.fetch(**kwargs)
        added = _persist_jobs(db, raws)
        return {"source": name, "fetched": len(raws), "added": added}
    finally:
        db.close()


# ---------- EMBEDDING ----------

@celery.task
def embed_missing_jobs(batch: int = 50):
    db = SessionLocal()
    try:
        jobs = db.query(Job).filter(Job.embedding.is_(None)).limit(batch).all()
        for j in jobs:
            try:
                embed_job(j)
            except Exception as e:
                print(f"[embed] job {j.id} failed: {e}")
        db.commit()
        return {"embedded": len(jobs)}
    finally:
        db.close()


@celery.task
def reembed_all_jobs():
    db = SessionLocal()
    try:
        jobs = db.query(Job).all()
        for j in jobs:
            try:
                embed_job(j)
            except Exception:
                pass
        db.commit()
        return {"reembedded": len(jobs)}
    finally:
        db.close()


# ---------- SEARCH SYNC ----------

@celery.task
def sync_meilisearch():
    db = SessionLocal()
    try:
        return sync_all_jobs_to_meili(db)
    finally:
        db.close()


# ---------- CLEANUP ----------

@celery.task
def deactivate_old_jobs(days: int = 60):
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        q = db.query(Job).filter(Job.is_active.is_(True), Job.posted_at < cutoff)
        n = q.update({"is_active": False}, synchronize_session=False)
        db.commit()
        return {"deactivated": n}
    finally:
        db.close()

@celery.task
def process_apply_queue(batch_size: int = 2):
    from app.autopilot.adapters import pick_adapter
    from app.autopilot.browser import Browser
    from app.autopilot.queue import pop_apply_tasks

    items = pop_apply_tasks(batch_size)
    if not items:
        return {"processed": 0}

    return asyncio.run(_run_applies(items))


async def _run_applies(items: list[dict]):
    db = SessionLocal()
    results = []
    try:
        async with Browser(headless=False, user_id="default") as browser:
            for it in items:
                job = db.get(Job, it["job_id"])
                vault = db.query(ProfileVault).filter_by(user_id=it["user_id"]).first()
                if not job or not vault:
                    results.append({"job": it.get("job_id"), "status": "missing"})
                    continue
                adapter = pick_adapter(job.url)
                if not adapter:
                    results.append({"job": str(job.id), "status": "no_adapter"})
                    continue
                page = await browser.context.new_page()
                try:
                    res = await adapter.apply(page, job, vault)
                    results.append({"job": str(job.id), "status": res.status, "msg": res.message})
                    app = db.query(Application).filter_by(
                        user_id=it["user_id"], job_id=job.id
                    ).first()
                    if not app:
                        app = Application(user_id=it["user_id"], job_id=job.id)
                        db.add(app)
                    app.status = "applied" if res.status == "submitted" else "prefill"
                    app.cover_letter = res.message
                    db.commit()
                except Exception as e:
                    results.append({"job": str(job.id), "status": "error", "msg": str(e)})
                finally:
                    await page.close()
    finally:
        db.close()
    return {"processed": len(items), "results": results}
