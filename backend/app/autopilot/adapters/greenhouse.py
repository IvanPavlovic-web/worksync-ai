from .base import ApplyResult, BaseAdapter
from app.autopilot.human import human_delay, human_type
from app.vault.filler import guess_value


class GreenhouseAdapter(BaseAdapter):
    name = "greenhouse"
    domain_pattern = r"greenhouse\.io"

    async def apply(self, page, job, vault) -> ApplyResult:
        await page.goto(job.url, wait_until="domcontentloaded")
        await human_delay()
        try:
            await page.click("a:has-text('Apply'), button:has-text('Apply')", timeout=5000)
        except Exception:
            pass
        await human_delay(0.8, 1.8)

        await self._fill_standard(page, vault)
        await self._upload_resume(page, vault)
        await self._answer_custom_questions(page, vault)
        await self._handle_demographics(page, vault)

        ss = f"./screenshots/{job.id}_gh.png"
        await page.screenshot(path=ss, full_page=True)
        return ApplyResult("needs_human", "Forma popunjena — klikni Submit.", ss)

    async def _fill_standard(self, page, vault):
        v = vault
        fields = {
            "input#first_name, input[name='first_name']": v.first_name,
            "input#last_name, input[name='last_name']": v.last_name,
            "input#email, input[name='email']": v.email,
            "input#phone, input[name='phone']": v.phone,
            "input#country, select#country": v.country,
            "input#job_application_location": v.city,
        }
        for sel, val in fields.items():
            if not val:
                continue
            try:
                loc = page.locator(sel).first
                tag = await loc.evaluate("el => el.tagName")
                if tag == "SELECT":
                    try:
                        await loc.select_option(label=str(val), timeout=1500)
                    except Exception:
                        pass
                else:
                    await human_type(loc, str(val))
            except Exception:
                continue

        for sel, val in [
            ("input[name*='LinkedIn']", v.linkedin_url),
            ("input[name*='GitHub']", v.github_url),
            ("input[name*='Portfolio'], input[name*='Website']", v.portfolio_url),
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
            await page.locator("input[type='file'][name*='resume']").first.set_input_files(vault.resume_url)
        except Exception:
            try:
                await page.locator("input[type='file']").first.set_input_files(vault.resume_url)
            except Exception:
                pass

    async def _answer_custom_questions(self, page, vault):
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
                if not await field.is_visible():
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
                    elif itype == "radio":
                        if "sponsor" in text.lower() and vault.requires_sponsorship:
                            name = await field.get_attribute("name")
                            try:
                                await page.locator(f"input[name='{name}'][value='Yes']").check()
                            except Exception:
                                pass
                    elif itype == "checkbox":
                        if "sponsor" in text.lower() and vault.requires_sponsorship:
                            try:
                                await field.check()
                            except Exception:
                                pass
                elif tag == "TEXTAREA":
                    val = guess_value(text, fid, vault)
                    if val:
                        await field.fill(str(val))
            except Exception:
                continue

    async def _handle_demographics(self, page, vault):
        for label_text, val in [
            ("Gender", vault.gender),
            ("Race", vault.ethnicity),
            ("Veteran", vault.veteran_status),
            ("Disability", vault.disability_status),
        ]:
            if not val:
                continue
            try:
                sel = page.locator(f"select:near(:text('{label_text}'))").first
                await sel.select_option(label=str(val), timeout=1000)
            except Exception:
                pass