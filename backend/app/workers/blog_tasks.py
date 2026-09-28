from datetime import datetime, timezone
from slugify import slugify
from app.database import SessionLocal
from app.models import BlogPost, Job
from app.workers.celery_app import celery

def _html(text: str) -> str:
    import bleach
    return bleach.clean(text.replace("\n\n", "</p><p>").replace("\n", "<br>"), tags=["p", "br", "strong", "h2"], attributes={}, strip=True)

@celery.task
def generate_blog_post(topic: str, keywords: list[str], locale: str = "bs"):
    db = SessionLocal()
    try:
        jobs = db.query(Job).filter(Job.is_active.is_(True)).order_by(Job.scraped_at.desc()).limit(5).all()
        title = topic.strip()[:180]; slug = slugify(title)[:150]; base = slug; index = 1
        while db.query(BlogPost).filter_by(slug=slug).first(): slug = f"{base}-{index}"; index += 1
        lines = [f"## {title}", "", "Ovaj vodič koristi aktuelne podatke iz baze oglasa i namijenjen je kandidatima koji planiraju sljedeći korak u karijeri.", "", "### Aktuelni oglasi", ""]
        lines.extend(f"- {j.title} - {j.company} ({j.location})" for j in jobs)
        content = "\n".join(lines)
        post = BlogPost(slug=slug, locale=locale, title=title, excerpt=f"Praktičan vodič: {title}.", content_md=content, content_html=_html(content), author="WorkSync", category="karijera", keywords=keywords, seo_title=title[:160], seo_description=f"{title}.", published=True)
        db.add(post); db.commit(); return {"ok": True, "slug": slug, "title": title}
    finally: db.close()

@celery.task
def generate_blog_batch(count: int = 3):
    topics = [("Kako pronaći posao u 2026", ["posao", "karijera"]), ("Vodič za kvalitetan CV", ["cv", "zaposlenje"]), ("Remote rad iz BiH", ["remote", "rad"])]
    return {"queued": len(topics[:count]), "tasks": [generate_blog_post.delay(t, k).id for t, k in topics[:count]]}
