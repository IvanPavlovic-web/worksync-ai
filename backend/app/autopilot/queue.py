import json
import time

import redis

from app.config import settings


r = redis.from_url(settings.REDIS_URL, decode_responses=True)

RATE_LIMITS = {
    "greenhouse": 15,
    "lever": 15,
    "ashby": 15,
    "workable": 15,
    "smartrecruiters": 15,
    "linkedin": 5,
    "default": 10,
}


def rate_limit_ok(source: str) -> bool:
    limit = RATE_LIMITS.get(source, RATE_LIMITS["default"])
    key = f"ratelimit:{source}:{int(time.time() // 3600)}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 3600)
    return count <= limit


def enqueue_apply(user_id: str, job_id: str, source: str) -> dict:
    if not rate_limit_ok(source):
        return {"queued": False, "reason": "rate_limit"}
    r.lpush("apply_queue", json.dumps({
        "user_id": user_id,
        "job_id": job_id,
        "source": source,
        "enqueued_at": time.time(),
    }))
    return {"queued": True}


def pop_apply_tasks(max_items: int = 3) -> list[dict]:
    out = []
    for _ in range(max_items):
        raw = r.rpop("apply_queue")
        if not raw:
            break
        try:
            out.append(json.loads(raw))
        except Exception:
            continue
    return out