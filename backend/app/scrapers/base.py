from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
import random, time
import httpx

@dataclass
class RawJob:
    source: str; external_id: str; title: str; company: str; url: str; description: str = ""; location: str = ""; salary_min: float | None = None; salary_max: float | None = None; currency: str | None = None; posted_at: datetime | None = None; raw: dict = field(default_factory=dict)

class BaseScraperV2(ABC):
    name = "base"; delay_seconds = 1.0; requires_playwright = False
    USER_AGENTS = ["WorkSyncBot/2.0 (+https://worksync.ba/bot)", "Mozilla/5.0 (compatible; WorkSyncBot/2.0)"]
    def __init__(self):
        self.user_agent = random.choice(self.USER_AGENTS)
        self.http = httpx.Client(timeout=httpx.Timeout(20.0, connect=8.0), headers={"User-Agent": self.user_agent, "Accept-Language": "en-US,en;q=0.9"}, follow_redirects=True)
        self._robots: dict[str, RobotFileParser] = {}
    @abstractmethod
    def fetch(self, **kwargs) -> list[RawJob]: ...
    def _respects_robots(self, url: str) -> bool:
        parsed = urlparse(url); root = f"{parsed.scheme}://{parsed.netloc}"
        if root not in self._robots:
            rp = RobotFileParser(); rp.set_url(urljoin(root, "/robots.txt"))
            try: rp.read()
            except Exception: return True
            self._robots[root] = rp
        return self._robots[root].can_fetch(self.user_agent, url)
    def _get(self, url: str, attempts: int = 3) -> httpx.Response:
        if not self._respects_robots(url): raise PermissionError(f"robots.txt disallows {url}")
        last = None
        for attempt in range(attempts):
            try:
                response = self.http.get(url)
                response.raise_for_status(); return response
            except (httpx.HTTPError, PermissionError) as exc:
                last = exc
                if isinstance(exc, PermissionError): raise
                if attempt < attempts - 1: time.sleep(min(8, 2 ** attempt) + random.random())
        raise last or RuntimeError("request failed")
    def _delay(self): time.sleep(self.delay_seconds + random.uniform(0, 0.5))
    @staticmethod
    def canonical_url(url: str) -> str:
        parsed = urlparse(url); return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), "", "", ""))
    @classmethod
    def deduplicate(cls, jobs: list[RawJob]) -> list[RawJob]:
        out, seen = [], set()
        for job in jobs:
            key = cls.canonical_url(job.url)
            if key and key not in seen: seen.add(key); out.append(job)
        return out

BaseScraper = BaseScraperV2
