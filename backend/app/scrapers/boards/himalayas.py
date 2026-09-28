from app.scrapers.base import BaseScraper, RawJob


class HimalayasScraper(BaseScraper):
    name = "himalayas"

    def fetch(self, limit: int = 100, **_) -> list[RawJob]:
        r = self.http.get(f"https://himalayas.app/jobs/api?limit={limit}")
        if r.status_code != 200:
            return []
        out: list[RawJob] = []
        for j in r.json().get("jobs", []):
            out.append(RawJob(
                source=self.name,
                external_id=str(j.get("id") or j.get("slug", "")),
                title=j.get("title", ""),
                company=j.get("companyName") or j.get("company", ""),
                url=j.get("applicationLink") or j.get("url", ""),
                description=j.get("description", "") or "",
                location=j.get("location") or "Remote",
                salary_min=j.get("minSalary"),
                salary_max=j.get("maxSalary"),
                currency=j.get("currency"),
                raw=j,
            ))
        return out