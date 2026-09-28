from bs4 import BeautifulSoup
from slugify import slugify

from app.scrapers.base import BaseScraper, RawJob


class HelloWorldRsScraper(BaseScraper):
    name = "helloworld.rs"
    delay_seconds = 2.0

    def fetch(self, max_pages: int = 5, **_) -> list[RawJob]:
        out: list[RawJob] = []
        seen: set[str] = set()
        for page in range(1, max_pages + 1):
            url = f"https://www.helloworld.rs/poslovi?page={page}"
            if not self._respects_robots(url):
                continue
            try:
                r = self.http.get(url)
                if r.status_code != 200:
                    break
                soup = BeautifulSoup(r.text, "lxml")
                cards = soup.select("a.job-link, article.job, .job-row")
                if not cards:
                    break
                for card in cards:
                    href = card.get("href") or (card.find("a") or {}).get("href")
                    if not href:
                        continue
                    if href.startswith("/"):
                        href = f"https://www.helloworld.rs{href}"
                    if href in seen:
                        continue
                    seen.add(href)
                    title = card.get_text(" ", strip=True)[:120]
                    out.append(RawJob(
                        source=self.name,
                        external_id=slugify(href.split("/")[-1] or href),
                        title=title,
                        company="",
                        url=href,
                        location="Srbija",
                    ))
                self._delay()
            except Exception as e:
                print(f"[helloworld.rs] {url} failed: {e}")
                break
        return out