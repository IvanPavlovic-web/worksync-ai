from datetime import datetime

from app.scrapers.base import BaseScraper, RawJob


class LeverScraper(BaseScraper):
    name = "lever"

    def fetch(self, boards: list[str] | None = None, **_):
        boards = boards or []
        out: list[RawJob] = []
        for board in boards:
            try:
                r = self.http.get(f"https://api.lever.co/v0/postings/{board}?mode=json")
                if r.status_code != 200:
                    continue
                for j in r.json():
                    posted = None
                    if j.get("createdAt"):
                        try:
                            posted = datetime.fromtimestamp(j["createdAt"] / 1000)
                        except Exception:
                            pass
                    cats = j.get("categories") or {}
                    out.append(RawJob(
                        source=self.name,
                        external_id=j["id"],
                        title=j["text"],
                        company=board,
                        url=j["hostedUrl"],
                        description=j.get("descriptionPlain", "") or "",
                        location=cats.get("location", ""),
                        posted_at=posted,
                        raw=j,
                    ))
            except Exception as e:
                print(f"[lever] {board} failed: {e}")
        return out