from app.scrapers.base import BaseScraper, RawJob


class WorkableScraper(BaseScraper):
    name = "workable"

    def fetch(self, boards: list[str] | None = None, **_):
        boards = boards or []
        out: list[RawJob] = []
        for board in boards:
            try:
                r = self.http.get(
                    f"https://apply.workable.com/api/v1/widget/accounts/{board}"
                )
                if r.status_code != 200:
                    continue
                for j in r.json().get("jobs", []):
                    loc = j.get("location") or {}
                    out.append(RawJob(
                        source=self.name,
                        external_id=j.get("shortcode", ""),
                        title=j.get("title", ""),
                        company=board,
                        url=j.get("url", ""),
                        description=j.get("description", "") or "",
                        location=loc.get("location_str", "") if isinstance(loc, dict) else "",
                        raw=j,
                    ))
            except Exception as e:
                print(f"[workable] {board} failed: {e}")
        return out