from app.scrapers.base import BaseScraper, RawJob


class SmartRecruitersScraper(BaseScraper):
    name = "smartrecruiters"

    def fetch(self, boards: list[str] | None = None, **_):
        boards = boards or []
        out: list[RawJob] = []
        for board in boards:
            try:
                r = self.http.get(
                    f"https://api.smartrecruiters.com/v1/companies/{board}/postings"
                )
                if r.status_code != 200:
                    continue
                for j in r.json().get("content", []):
                    loc = j.get("location") or {}
                    city = loc.get("city") or ""
                    country = loc.get("country") or ""
                    out.append(RawJob(
                        source=self.name,
                        external_id=j.get("id", ""),
                        title=j.get("name", ""),
                        company=board,
                        url=f"https://jobs.smartrecruiters.com/{board}/{j.get('id', '')}",
                        description="",
                        location=f"{city}, {country}".strip(", "),
                        raw=j,
                    ))
            except Exception as e:
                print(f"[smartrecruiters] {board} failed: {e}")
        return out