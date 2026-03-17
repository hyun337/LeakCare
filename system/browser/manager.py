from playwright.async_api import async_playwright
from system.browser.stealth import stealth_async

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
        )
        page = await context.new_page()
        await stealth_async(page)
        return page

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
