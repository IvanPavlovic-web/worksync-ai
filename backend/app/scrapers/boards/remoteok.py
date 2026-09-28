from datetime import datetime

from app.scrapers.base import BaseScraper, RawJob


class RemoteOKScraper(BaseScraper):
    name = "remoteok"

    def fetch(self, limit: int = 100, **_) -> list[RawJob]:
        r = self.http.get("https://remoteok.com/api", headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []
        data = r.json()
        # Prvi element je meta, ostalo su poslovi
        items = [x for x in data if isinstance(x, dict) and x.get("id")]
        out: list[RawJob] = []
        for j in items[:limit]:
            posted = None
            if j.get("date"):
                try:
                    posted = datetime.fromisoformat(j["date"].replace("Z", "+00:00"))
                except Exception:
                    pass
            out.append(RawJob(
                source=self.name,
                external_id=str(j.get("id")),
                title=j.get("position", ""),
                company=j.get("company", ""),
                url=j.get("url", ""),
                description=j.get("description", "") or "",
                location=j.get("location") or "Remote",
                salary_min=j.get("salary_min"),
                salary_max=j.get("salary_max"),
                posted_at=posted,
                raw=j,
            ))
        return out