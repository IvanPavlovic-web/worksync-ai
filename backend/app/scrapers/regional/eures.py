from app.scrapers.base import BaseScraper, RawJob


class EURESScraper(BaseScraper):
    name = "eures"
    API = "https://ec.europa.eu/eures/eures-apps/searchengine/page/jv-search/search"

    def fetch(self, keyword: str = "developer", country: str = "de", **_) -> list[RawJob]:
        try:
            r = self.http.post(
                self.API,
                json={
                    "resultsPerPage": 50,
                    "page": 0,
                    "sortSearch": "BEST_MATCH",
                    "keywords": [{"keyword": keyword, "specificSearchCode": "EVERYWHERE"}],
                    "locationCodes": [country.upper()],
                    "publicationPeriod": "LAST_WEEK",
                },
                headers={"Content-Type": "application/json"},
            )
            if r.status_code != 200:
                return []
            out: list[RawJob] = []
            for j in r.json().get("jvs", []):
                out.append(RawJob(
                    source=self.name,
                    external_id=str(j.get("id", "")),
                    title=j.get("title", ""),
                    company=(j.get("employer") or {}).get("name", ""),
                    url=f"https://ec.europa.eu/eures/portal/jv-se/jv-details/{j.get('id', '')}",
                    location=(j.get("locationMap") or {}).get("region", ""),
                    description=j.get("description", "") or "",
                    raw=j,
                ))
            return out
        except Exception as e:
            print(f"[eures] {keyword}/{country} failed: {e}")
            return []