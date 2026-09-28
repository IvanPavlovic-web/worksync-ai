from .base import ApplyResult, BaseAdapter
from app.autopilot.human import human_delay, human_type


class AshbyAdapter(BaseAdapter):
    name = "ashby"
    domain_pattern = r"ashbyhq\.com|jobs\.ashbyhq\.com"

    async def apply(self, page, job, vault) -> ApplyResult:
        await page.goto(job.url, wait_until="domcontentloaded")
        await human_delay(1.5, 3)

        # Klikni "Apply for this Job" ako postoji
        for sel in [
            "a:has-text('Apply for this Job')",
            "button:has-text('Apply for this Job')",
            "a:has-text('Apply')",
            "button:has-text('Apply')",
        ]:
            try:
                await page.click(sel, timeout=3000)
                await human_delay(0.8, 1.6)
                break
            except Exception:
                continue

        await self._fill_standard(page, vault)
        await self._upload_resume(page, vault)
        await self._answer_questions(page, vault)

        ss = f"./screenshots/{job.id}_ashby.png"
        await page.screenshot(path=ss, full_page=True)
        return ApplyResult("needs_human", "Ashby forma popunjena — provjeri i Submit.", ss)

    async def _fill_standard(self, page, vault):
        fields = [
            ("input[name='_systemfield_name']", f"{vault.first_name or ''} {vault.last_name or ''}".strip()),
            ("input[name='_systemfield_email']", vault.email or ""),
            ("input[name='_systemfield_phone']", vault.phone or ""),
            ("input[name='name']", f"{vault.first_name or ''} {vault.last_name or ''}".strip()),
            ("input[name='email']", vault.email or ""),
            ("input[name='phone']", vault.phone or ""),
            ("input[autocomplete='given-name']", vault.first_name or ""),
            ("input[autocomplete='family-name']", vault.last_name or ""),
            ("input[autocomplete='email']", vault.email or ""),
            ("input[autocomplete='tel']", vault.phone or ""),
            ("input[name*='linkedin' i]", vault.linkedin_url or ""),
            ("input[name*='github' i]", vault.github_url or ""),
            ("input[name*='website' i]", vault.portfolio_url or ""),
        ]
        for sel, val in fields:
            if not val:
                continue
            try:
                loc = page.locator(sel).first
                if await loc.count() and await loc.is_visible():
                    await human_type(loc, str(val))
            except Exception:
                continue

        # Polje "Location" (Ashby tipično ima autocomplete grad)
        try:
            loc_input = page.locator("input[name*='location' i]").first
            if await loc_input.count() and vault.city:
                await human_type(loc_input, f"{vault.city}, {vault.country or ''}".strip(", "))
                await human_delay(0.5, 1.2)
                # Odaberi prvi predlog
                try:
                    await page.locator("ul[role='listbox'] li").first.click(timeout=2000)
                except Exception:
                    pass
        except Exception:
            pass

    async def _upload_resume(self, page, vault):
        if not vault.resume_url:
            return
        try:
            inputs = await page.locator("input[type='file']").all()
            if inputs:
                await inputs[0].set_input_files(vault.resume_url)
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
                    if not await field.count() or not await field.is_visible():
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
                                    await page.locator(f"input[name='{name}'][value*='Yes' i]").check()
                                except Exception:
                                    pass
                    elif tag == "TEXTAREA":
                        val = guess_value(text, fid, vault)
                        if val:
                            await field.fill(str(val))
                except Exception:
                    continue
        except Exception:
            pass