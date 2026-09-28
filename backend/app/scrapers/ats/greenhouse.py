from datetime import datetime

from app.scrapers.base import BaseScraper, RawJob


class GreenhouseScraper(BaseScraper):
    name = "greenhouse"

    def fetch(self, boards: list[str] | None = None, **_):
        boards = boards or []
        out: list[RawJob] = []
        for board in boards:
            try:
                r = self.http.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
                )
                if r.status_code != 200:
                    continue
                for j in r.json().get("jobs", []):
                    posted = None
                    if j.get("updated_at"):
                        try:
                            posted = datetime.fromisoformat(j["updated_at"].replace("Z", "+00:00"))
                        except Exception:
                            posted = None
                    out.append(RawJob(
                        source=self.name,
                        external_id=str(j["id"]),
                        title=j["title"],
                        company=board,
                        url=j["absolute_url"],
                        description=j.get("content", "") or "",
                        location=(j.get("location") or {}).get("name", ""),
                        posted_at=posted,
                        raw=j,
                    ))
            except Exception as e:
                print(f"[greenhouse] {board} failed: {e}")
        return out