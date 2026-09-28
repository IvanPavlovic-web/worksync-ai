import math
import re
from app.ai.embedder import build_profile_text
from app.models import Job, Profile

def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b: return 0.0
    denom = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b))
    return max(0.0, min(1.0, sum(x*y for x, y in zip(a, b)) / (denom or 1)))

def hybrid_match(db, profile: Profile, limit: int = 30):
    terms = set(re.findall(r"[\w+#.-]{2,}", build_profile_text(profile).lower()))
    results = []
    for job in db.query(Job).filter(Job.is_active.is_(True)).all():
        text = f"{job.title} {job.description} {job.category or ''} {job.keywords or ''}".lower()
        keywords = set(re.findall(r"[\w+#.-]{2,}", text))
        overlap = len(terms & keywords) / max(1, len(terms))
        vector = _cosine(profile.embedding or [], job.embedding or [])
        results.append({"job": job, "vector_score": vector, "keyword_score": overlap, "final_score": 0.7 * vector + 0.3 * overlap})
    return sorted(results, key=lambda x: x["final_score"], reverse=True)[:limit]
