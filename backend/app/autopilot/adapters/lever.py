from .base import ApplyResult, BaseAdapter
from app.autopilot.human import human_delay


class LeverAdapter(BaseAdapter):
    name = "lever"
    domain_pattern = r"jobs\.lever\.co"

    async def apply(self, page, job, vault) -> ApplyResult:
        await page.goto(job.url.rstrip("/") + "/apply", wait_until="domcontentloaded")
        await human_delay(1, 2)
        try:
            await page.fill("input[name='name']", f"{vault.first_name or ''} {vault.last_name or ''}".strip())
            await page.fill("input[name='email']", vault.email or "")
            if vault.phone:
                await page.fill("input[name='phone']", vault.phone)
            if vault.linkedin_url:
                await page.fill("input[name='urls[LinkedIn]']", vault.linkedin_url)
            if vault.github_url:
                await page.fill("input[name='urls[GitHub]']", vault.github_url)
            if vault.portfolio_url:
                await page.fill("input[name='urls[Portfolio]']", vault.portfolio_url)
            if vault.resume_url:
                await page.locator("input[type='file']").first.set_input_files(vault.resume_url)
        except Exception as e:
            return ApplyResult("failed", str(e))
        ss = f"./screenshots/{job.id}_lever.png"
        await page.screenshot(path=ss, full_page=True)
        return ApplyResult("needs_human", "Popunjeno — klikni Submit.", ss)