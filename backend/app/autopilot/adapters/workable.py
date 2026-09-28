from .base import ApplyResult, BaseAdapter
from app.autopilot.human import human_delay, human_type


class WorkableAdapter(BaseAdapter):
    name = "workable"
    domain_pattern = r"apply\.workable\.com|jobs\.workable\.com"

    async def apply(self, page, job, vault) -> ApplyResult:
        await page.goto(job.url, wait_until="domcontentloaded")
        await human_delay(1.5, 3)

        # Klikni "Apply for this job"
        for sel in [
            "a:has-text('Apply for this job')",
            "button:has-text('Apply for this job')",
            "a:has-text('Apply')",
            "button:has-text('Apply')",
        ]:
            try:
                await page.click(sel, timeout=3000)
                await human_delay(1, 2)
                break
            except Exception:
                continue

        await self._fill_standard(page, vault)
        await self._upload_resume(page, vault)
        await self._answer_questions(page, vault)

        ss = f"./screenshots/{job.id}_workable.png"
        await page.screenshot(path=ss, full_page=True)
        return ApplyResult("needs_human", "Workable forma popunjena — provjeri i Submit.", ss)

    async def _fill_standard(self, page, vault):
        # Workable tipično: first, last, email, phone
        try:
            await page.fill("input[name='firstname'], input#firstname", vault.first_name or "")
        except Exception:
            pass
        try:
            await page.fill("input[name='lastname'], input#lastname", vault.last_name or "")
        except Exception:
            pass
        try:
            await page.fill("input[name='email'], input#email", vault.email or "")
        except Exception:
            pass
        try:
            if vault.phone:
                await page.fill("input[name='phone'], input#phone", vault.phone)
        except Exception:
            pass

        # Adresa
        for sel, val in [
            ("input[name='address']", vault.address_line1),
            ("input[name='city']", vault.city),
            ("input[name='postal']", vault.postal_code),
            ("input[name='country']", vault.country),
        ]:
            if not val:
                continue
            try:
                await page.fill(sel, val, timeout=1500)
            except Exception:
                pass

        # LinkedIn / portfolio
        for sel, val in [
            ("input[name*='linkedin' i]", vault.linkedin_url),
            ("input[name*='github' i]", vault.github_url),
            ("input[name*='website' i], input[name*='portfolio' i]", vault.portfolio_url),
        ]:
            if val:
                try:
                    await page.fill(sel, val, timeout=1500)
                except Exception:
                    pass

    async def _upload_resume(self, page, vault):
        if not vault.resume_url:
            return
        try:
            await page.locator("input[type='file']").first.set_input_files(vault.resume_url)
            await human_delay(1.5, 3)
        except Exception:
            pass

    async def _answer_questions(self, page, vault):
        from app.vault.filler import guess_value
        try:
            labels = await page.locator("label").all()
            for lbl in labels:
                try:
                    text = (await lbl.inner_text()).strip()
                    if not text:
                        continue
                    fid = await lbl.get_attribute("for")
                    if not fid:
                        continue
                    field = page.locator(f"#{fid}").first
                    if not await field.count():
                        continue
                    tag = await field.evaluate("el => el.tagName")
                    if tag == "SELECT":
                        val = guess_value(text, fid, vault)
                        if val is not None:
                            try:
                                await field.select_option(label=str(val), timeout=1000)
                            except Exception:
                                pass
                    elif tag == "INPUT":
                        itype = (await field.get_attribute("type")) or "text"
                        if itype in ("text", "email", "tel", "number", "url"):
                            val = guess_value(text, fid, vault)
                            if val is not None:
                                await field.fill(str(val))
                    elif tag == "TEXTAREA":
                        val = guess_value(text, fid, vault)
                        if val:
                            await field.fill(str(val))
                except Exception:
                    continue
        except Exception:
            pass