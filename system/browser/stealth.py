async def stealth_async(page):
    """
    사이트에서 자동화 브라우저(봇) 탐지를 우회하기 위한 설정
    """

    await page.add_init_script("""
        // webdriver 감지 제거
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });

        // chrome 객체 추가 (일부 사이트 필수)
        window.chrome = {runtime: {}};

        // 플러그인 존재하는 것처럼 위장
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3]
        });

        // 언어 설정 (한국 사용자처럼 보이기)
        Object.defineProperty(navigator, 'languages', {
            get: () => ['ko-KR', 'ko']
        });
    """)
