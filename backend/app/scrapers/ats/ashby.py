from app.scrapers.base import BaseScraper, RawJob


QUERY = """
query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
  jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) {
    jobPostings {
      id
      title
      locationName
      employmentType
      jobUrl
      descriptionPlain
    }
  }
}
"""


class AshbyScraper(BaseScraper):
    name = "ashby"

    def fetch(self, boards: list[str] | None = None, **_):
        boards = boards or []
        out: list[RawJob] = []
        for board in boards:
            try:
                r = self.http.post(
                    "https://api.ashbyhq.com/posting-api/job-board/graphql",
                    json={
                        "operationName": "ApiJobBoardWithTeams",
                        "variables": {"organizationHostedJobsPageName": board},
                        "query": QUERY,
                    },
                )
                if r.status_code != 200:
                    continue
                postings = (
                    r.json().get("data", {}).get("jobBoard", {}) or {}
                ).get("jobPostings", []) or []
                for j in postings:
                    out.append(RawJob(
                        source=self.name,
                        external_id=j["id"],
                        title=j["title"],
                        company=board,
                        url=j["jobUrl"],
                        description=j.get("descriptionPlain", "") or "",
                        location=j.get("locationName", ""),
                        raw=j,
                    ))
            except Exception as e:
                print(f"[ashby] {board} failed: {e}")
        return out