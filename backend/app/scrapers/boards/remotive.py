from datetime import datetime
import re

from app.scrapers.base import BaseScraper, RawJob


def parse_salary(s: str) -> tuple[float | None, float | None]:
    if not s:
        return None, None
    nums = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]+", s)]
    if not nums:
        return None, None
    if len(nums) == 1:
        return float(nums[0]), float(nums[0])
    return float(nums[0]), float(nums[1])


class RemotiveScraper(BaseScraper):
    name = "remotive"

    def fetch(self, **_) -> list[RawJob]:
        r = self.http.get("https://remotive.com/api/remote-jobs")
        if r.status_code != 200:
            return []
        out: list[RawJob] = []
        for j in r.json().get("jobs", []):
            smin, smax = parse_salary(j.get("salary", ""))
            posted = None
            if j.get("publication_date"):
                try:
                    posted = datetime.fromisoformat(j["publication_date"])
                except Exception:
                    pass
            out.append(RawJob(
                source=self.name,
                external_id=str(j["id"]),
                title=j["title"],
                company=j["company_name"],
                url=j["url"],
                description=j.get("description", "") or "",
                location=j.get("candidate_required_location", "Remote"),
                salary_min=smin,
                salary_max=smax,
                posted_at=posted,
                raw=j,
            ))
        return out