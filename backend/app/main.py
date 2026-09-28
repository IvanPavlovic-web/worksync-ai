from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api import (
    ai, applications, auth, blog, jobs, profile, public, search,
)
from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="WorkSync AI", version="2.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Javni (SEO)
app.include_router(public.router, prefix="/api/public", tags=["public"])
app.include_router(blog.router, prefix="/api/blog", tags=["blog"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

# Auth
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/api/applications", tags=["applications"])


@app.get("/health")
def health():
    return {"ok": True, "version": "2.0"}

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
