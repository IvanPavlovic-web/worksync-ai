from datetime import datetime

from app.scrapers.base import BaseScraper, RawJob


class ArbeitnowScraper(BaseScraper):
    name = "arbeitnow"

    def fetch(self, limit: int = 100, **_) -> list[RawJob]:
        r = self.http.get("https://www.arbeitnow.com/api/job-board-api")
        if r.status_code != 200:
            return []
        data = r.json().get("data", [])[:limit]
        out: list[RawJob] = []
        for j in data:
            posted = None
            if j.get("created_at"):
                try:
                    posted = datetime.fromtimestamp(j["created_at"])
                except Exception:
                    pass
            out.append(RawJob(
                source=self.name,
                external_id=j.get("slug", ""),
                title=j.get("title", ""),
                company=j.get("company_name", ""),
                url=j.get("url", ""),
                description=j.get("description", "") or "",
                location=j.get("location", ""),
                posted_at=posted,
                raw=j,
            ))
        return out