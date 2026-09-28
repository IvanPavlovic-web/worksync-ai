from datetime import datetime

from app.scrapers.base import BaseScraper, RawJob


class JobicyScraper(BaseScraper):
    name = "jobicy"

    def fetch(self, count: int = 100, **_) -> list[RawJob]:
        r = self.http.get(f"https://jobicy.com/api/v2/remote-jobs?count={count}")
        if r.status_code != 200:
            return []
        out: list[RawJob] = []
        for j in r.json().get("jobs", []):
            posted = None
            if j.get("pubDate"):
                try:
                    posted = datetime.fromisoformat(j["pubDate"].replace("Z", "+00:00"))
                except Exception:
                    pass
            out.append(RawJob(
                source=self.name,
                external_id=str(j["id"]),
                title=j["jobTitle"],
                company=j["companyName"],
                url=j["url"],
                description=j.get("jobDescription", "") or "",
                location=j.get("jobGeo", "Remote"),
                salary_min=j.get("annualSalaryMin"),
                salary_max=j.get("annualSalaryMax"),
                currency=j.get("salaryCurrency"),
                posted_at=posted,
                raw=j,
            ))
        return out