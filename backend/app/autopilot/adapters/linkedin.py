from .base import ApplyResult, BaseAdapter
from app.autopilot.human import human_delay


class LinkedInAdapter(BaseAdapter):
    name = "linkedin"
    domain_pattern = r"linkedin\.com/jobs"

    async def apply(self, page, job, vault) -> ApplyResult:
        await page.goto(job.url, wait_until="domcontentloaded")
        await human_delay(2, 4)
        if "login" in page.url or "authwall" in page.url:
            return ApplyResult("needs_human", "Prijavi se ručno na LinkedIn pa pokreni ponovo.")
        try:
            await page.click("button.jobs-apply-button", timeout=5000)
        except Exception:
            return ApplyResult("skipped", "Nema Easy Apply dugmeta.")
        await human_delay(1.5, 3)
        try:
            if vault.phone:
                await page.fill("input[id*='phoneNumber']", vault.phone)
            if vault.resume_url:
                await page.locator("input[type='file']").first.set_input_files(vault.resume_url)
        except Exception:
            pass
        ss = f"./screenshots/{job.id}_li.png"
        await page.screenshot(path=ss, full_page=True)
        return ApplyResult(
            "needs_human",
            "⚠️ LinkedIn: forma popunjena ali NE klikći Submit automatski.",
            ss,
        )