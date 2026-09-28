from bs4 import BeautifulSoup
from slugify import slugify

from app.scrapers.base import BaseScraper, RawJob


class MakeItInGermanyScraper(BaseScraper):
    name = "make-it-in-germany"
    delay_seconds = 2.0

    def fetch(self, **_) -> list[RawJob]:
        url = "https://www.make-it-in-germany.com/en/jobs/"
        if not self._respects_robots(url):
            return []
        try:
            r = self.http.get(url)
            if r.status_code != 200:
                return []
            soup = BeautifulSoup(r.text, "lxml")
            out: list[RawJob] = []
            for card in soup.select(".job-listing-item, [data-job-id]"):
                link = card.find("a", href=True)
                if not link:
                    continue
                href = link["href"]
                if href.startswith("/"):
                    href = f"https://www.make-it-in-germany.com{href}"
                title_el = card.select_one(".job-title, h3, h4")
                company_el = card.select_one(".company-name, .employer")
                out.append(RawJob(
                    source=self.name,
                    external_id=slugify(href.split("/")[-1] or href),
                    title=title_el.get_text(strip=True) if title_el else "",
                    company=company_el.get_text(strip=True) if company_el else "",
                    url=href,
                    location="Njemačka",
                ))
            return out
        except Exception as e:
            print(f"[make-it-in-germany] failed: {e}")
            return []