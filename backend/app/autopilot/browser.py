from playwright.async_api import async_playwright


class Browser:
    def __init__(self, headless: bool = False, user_id: str = "default"):
        self.headless = headless
        self.user_id = user_id
        self.data_dir = f"./.pw_profiles/{user_id}"
        self.pw = None
        self.context = None

    async def __aenter__(self):
        self.pw = await async_playwright().start()
        self.context = await self.pw.chromium.launch_persistent_context(
            self.data_dir,
            headless=self.headless,
            viewport={"width": 1440, "height": 900},
            locale="bs-BA",
            timezone_id="Europe/Sarajevo",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {}, loadTimes: () => {}, csi: () => {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['bs','hr','sr','en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
        """)
        return self

    async def __aexit__(self, *args):
        if self.context:
            await self.context.close()
        if self.pw:
            await self.pw.stop()