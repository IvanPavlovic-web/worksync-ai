from datetime import datetime

import feedparser

from app.scrapers.base import BaseScraper, RawJob


class WWRScraper(BaseScraper):
    name = "weworkremotely"

    FEEDS = {
        "programming": "https://weworkremotely.com/categories/remote-programming-jobs.rss",
        "devops": "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
        "design": "https://weworkremotely.com/categories/remote-design-jobs.rss",
        "product": "https://weworkremotely.com/categories/remote-product-jobs.rss",
        "marketing": "https://weworkremotely.com/categories/remote-marketing-jobs.rss",
        "customer-support": "https://weworkremotely.com/categories/remote-customer-support-jobs.rss",
    }

    def fetch(self, **_) -> list[RawJob]:
        out: list[RawJob] = []
        for cat, url in self.FEEDS.items():
            try:
                feed = feedparser.parse(url)
                for e in feed.entries:
                    title_raw = e.title or ""
                    if ":" in title_raw:
                        company, title = title_raw.split(":", 1)
                    else:
                        company, title = "", title_raw
                    posted = None
                    if e.get("published_parsed"):
                        try:
                            posted = datetime(*e.published_parsed[:6])
                        except Exception:
                            pass
                    out.append(RawJob(
                        source=self.name,
                        external_id=e.get("id", e.link),
                        title=title.strip(),
                        company=company.strip(),
                        url=e.link,
                        description=e.get("summary", "") or "",
                        location="Remote",
                        posted_at=posted,
                        raw={"category": cat},
                    ))
            except Exception as e:
                print(f"[wwr] {cat} failed: {e}")
        return out