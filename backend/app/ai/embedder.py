from functools import lru_cache
from app.config import settings
from app.models import Job, Profile

@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.EMBEDDING_MODEL)

def embed(text: str) -> list[float]:
    return _model().encode(text, normalize_embeddings=True).tolist()

def build_profile_text(profile: Profile) -> str:
    parts = [profile.title or "", profile.summary or "", profile.seniority or "", ", ".join(s.name for s in profile.skills or [])]
    for exp in profile.experiences or []:
        parts.extend([f"{exp.role} @ {exp.company} {(exp.description or '')[:1000]}", ", ".join(exp.technologies or [])])
    return "\n".join(x for x in parts if x)[:8000]

def build_job_text(job: Job) -> str:
    return "\n".join(x for x in [job.title, job.company, job.location, job.work_mode, job.seniority or "", job.category or "", (job.description or "")[:6000]] if x)

def embed_profile(profile: Profile) -> None:
    text = build_profile_text(profile)
    if text.strip(): profile.embedding = embed(text)

def embed_job(job: Job) -> None:
    text = build_job_text(job)
    if text.strip(): job.embedding = embed(text)
