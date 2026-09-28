from bs4 import BeautifulSoup
from slugify import slugify

from app.scrapers.base import BaseScraper, RawJob


class PosaoHrScraper(BaseScraper):
    name = "posao.hr"
    delay_seconds = 2.0

    CATEGORIES = [
        "https://www.posao.hr/poslovi/informatika/",
        "https://www.posao.hr/poslovi/prodaja/",
        "https://www.posao.hr/poslovi/marketing/",
    ]

    def fetch(self, max_pages: int = 5, **_) -> list[RawJob]:
        out: list[RawJob] = []
        seen: set[str] = set()
        for cat_url in self.CATEGORIES:
            for page in range(1, max_pages + 1):
                url = f"{cat_url}?page={page}" if page > 1 else cat_url
                if not self._respects_robots(url):
                    continue
                try:
                    r = self.http.get(url)
                    if r.status_code != 200:
                        break
                    soup = BeautifulSoup(r.text, "lxml")
                    cards = soup.select("article.job, .job-item, li.job")
                    if not cards:
                        break
                    for card in cards:
                        link = card.find("a", href=True)
                        if not link:
                            continue
                        href = link["href"]
                        if href.startswith("/"):
                            href = f"https://www.posao.hr{href}"
                        if href in seen:
                            continue
                        seen.add(href)
                        title_el = card.select_one("h2, h3, .title")
                        company_el = card.select_one(".company, .employer")
                        title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
                        if not title:
                            continue
                        out.append(RawJob(
                            source=self.name,
                            external_id=slugify(href.split("/")[-2] if href.endswith("/") else href.split("/")[-1]),
                            title=title,
                            company=company_el.get_text(strip=True) if company_el else "",
                            url=href,
                            location="Hrvatska",
                        ))
                    self._delay()
                except Exception as e:
                    print(f"[posao.hr] {url} failed: {e}")
                    break
        return out