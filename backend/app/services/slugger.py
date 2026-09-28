from slugify import slugify

from app.models import Job


def unique_job_slug(db, title: str, company: str | None, exclude_id=None) -> str:
    base = slugify(f"{title}-{company or 'job'}")[:80] or "posao"
    slug = base
    i = 1
    while True:
        q = db.query(Job).filter_by(slug=slug)
        if exclude_id is not None:
            q = q.filter(Job.id != exclude_id)
        if not q.first():
            return slug
        slug = f"{base}-{i}"
        i += 1