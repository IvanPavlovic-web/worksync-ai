from bs4 import BeautifulSoup
from slugify import slugify

from app.scrapers.base import BaseScraper, RawJob


class PosaoBaScraper(BaseScraper):
    name = "posao.ba"
    delay_seconds = 2.0

    CATEGORIES = [
        "https://www.posao.ba/poslovi/informatika-telekomunikacije",
        "https://www.posao.ba/poslovi/ekonomija-finansije",
        "https://www.posao.ba/poslovi/trgovina-prodaja",
        "https://www.posao.ba/poslovi/ugostiteljstvo-turizam",
        "https://www.posao.ba/poslovi/gradevinarstvo",
        "https://www.posao.ba/poslovi/administracija",
        "https://www.posao.ba/poslovi/marketing",
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
                    cards = soup.select("a.job-item, article.job, .job-listing-item")
                    if not cards:
                        break
                    for card in cards:
                        href = card.get("href") or (card.find("a") or {}).get("href")
                        if not href:
                            continue
                        if href.startswith("/"):
                            href = f"https://www.posao.ba{href}"
                        if href in seen:
                            continue
                        seen.add(href)

                        title_el = card.select_one(".job-title, h3, h2")
                        company_el = card.select_one(".company, .employer")
                        loc_el = card.select_one(".location, .job-location")

                        title = title_el.get_text(strip=True) if title_el else ""
                        if not title:
                            continue

                        out.append(RawJob(
                            source=self.name,
                            external_id=slugify(href.split("/")[-1]),
                            title=title,
                            company=company_el.get_text(strip=True) if company_el else "",
                            url=href,
                            location=loc_el.get_text(strip=True) if loc_el else "Bosna i Hercegovina",
                            description="",
                        ))
                    self._delay()
                except Exception as e:
                    print(f"[posao.ba] {url} failed: {e}")
                    break
        return out