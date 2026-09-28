from app.scrapers.base import BaseScraper, RawJob

class CatalogScraper(BaseScraper):
    """Adapter for sources configured through RSS/JSON URLs, with safe defaults."""
    def __init__(self, source: str, endpoint: str | None = None):
        super().__init__(); self.name = source; self.endpoint = endpoint
    def fetch(self, **_) -> list[RawJob]:
        if not self.endpoint: return []
        response = self._get(self.endpoint)
        content_type = response.headers.get("content-type", "")
        if "json" not in content_type: return []
        items = response.json() if isinstance(response.json(), list) else response.json().get("jobs", [])
        return self.deduplicate([RawJob(source=self.name, external_id=str(item.get("id") or item.get("url")), title=item.get("title", ""), company=item.get("company", ""), url=item.get("url", ""), description=item.get("description", ""), location=item.get("location", "")) for item in items if item.get("url") and item.get("title")])
