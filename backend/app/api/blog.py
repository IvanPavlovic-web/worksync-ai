from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BlogPost


router = APIRouter()


def _post_to_dict(p: BlogPost, with_content: bool = False) -> dict:
    d = {
        "id": str(p.id),
        "slug": p.slug,
        "locale": p.locale,
        "title": p.title,
        "excerpt": p.excerpt,
        "cover_image": p.cover_image,
        "author": p.author,
        "category": p.category,
        "keywords": p.keywords,
        "seo_title": p.seo_title,
        "seo_description": p.seo_description,
        "published_at": p.published_at.isoformat(),
        "updated_at": p.updated_at.isoformat(),
        "views": p.views,
    }
    if with_content:
        d["content_html"] = p.content_html
        d["content_md"] = p.content_md
    return d


@router.get("")
def list_posts(locale: str = "bs", limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    q = db.query(BlogPost).filter(BlogPost.published.is_(True), BlogPost.locale == locale)
    total = q.count()
    posts = q.order_by(desc(BlogPost.published_at)).limit(limit).offset(offset).all()
    return {"total": total, "items": [_post_to_dict(p) for p in posts]}


@router.get("/sitemap")
def blog_sitemap(db: Session = Depends(get_db)):
    posts = db.query(BlogPost).filter(BlogPost.published.is_(True)).all()
    return [{"slug": p.slug, "updated_at": p.updated_at.isoformat()} for p in posts]


@router.get("/{slug}")
def get_post(slug: str, db: Session = Depends(get_db)):
    p = db.query(BlogPost).filter_by(slug=slug, published=True).first()
    if not p:
        raise HTTPException(404)
    p.views = (p.views or 0) + 1
    db.commit()
    return _post_to_dict(p, with_content=True)