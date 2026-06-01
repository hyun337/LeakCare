import random
from playwright.async_api import async_playwright
from system.browser.stealth import stealth_async


class BrowserManager:
    """
    Playwright 브라우저 실행/종료 관리 클래스
    """
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self, record_video=None):
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-infobars",
                "--disable-extensions",
            ]
        )

        context_args = {
            'viewport': {'width': 1280, 'height': 800},
            'user_agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            'locale': 'ko-KR',
            'timezone_id': 'Asia/Seoul',
        }

        if record_video:
            context_args["record_video_dir"] = record_video
            context_args["record_video_size"] = {"width": 1280, "height": 720}

        context = await self.browser.new_context(**context_args)

        async def intercept_route(route):
            req = route.request
            resource_type = req.resource_type
            url = req.url.lower()
            
            if resource_type in ["fetch", "xhr"]:
                return await route.continue_()
                
            if resource_type in ["font", "media"]:
                return await route.abort()
                
            bad_domains = ["google-analytics.com", "doubleclick.net", "facebook.net"]
            if any(domain in url for domain in bad_domains):
                return await route.abort()
                
            await route.continue_()
            
        # 모든 요청에 대해 필터링 규칙 적용
        await context.route("**/*", intercept_route)
        
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = await context.new_page()
        await stealth_async(page)
        return page

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
