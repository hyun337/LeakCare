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

        # 실제 브라우저와 유사한 인자 추가
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                "-- disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-inforbars"
            ]
        )

        # 1. 실제 사용자의 다양한 User-Agent 풀 구성
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Edge/122.0.2365.92"
        ]

        # 2. 컨텍스트 설정 강화 (언어, 타임존 등 추가)
        context_args = {
            'viewport': {'width': 1280, 'height': 800},
            'user_agent': random.choice(user_agents), # 실행 시마다 랜덤
            'locale': 'ko-KR',
            'timezone_id': 'Asia/Seoul',
            'permissions': ['geolocation'] # 실제 브라우저처럼 권한 설정 포함
        }
        
        if record_video:
            context_args["record_video_dir"] = record_video
            context_args["record_video_size"] = {"width": 1280, "height": 720}

        # 3. 설정된 인자로 컨텍스트 생성
        context = await self.browser.new_context(**context_args)

        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page = await context.new_page()

        # 봇 탐지 우회 적용
        await stealth_async(page)

        return page

    async def stop(self):
        """
        브라우저 종료 (이 시점에 동영상 파일이 최종 저장됩니다)
        """
        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()
