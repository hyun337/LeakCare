import asyncio

async def auto_scroll(page):
    """
    페이지 하단까지 자동 스크롤
    → lazy loading(지연 로딩 이미지) 활성화 목적
    """
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 300;

                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;

                    window.scrollBy(0, distance);
                    totalHeight += distance;

                    // 끝까지 도달하면 종료
                    if(totalHeight >= scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 200);
            });
        }
    """)


async def take_screenshot(page, url, output_path):
    """
    페이지 접속 → 스크롤 → 정리 → 전체 스크린샷
    """

    print(f"🌐 {url} 접속 중...")

    # 페이지 완전히 로딩될 때까지 대기
    response = await page.goto(url, wait_until="load")

    # ▼ 중요: 스크롤해야 이미지 다 뜸
    await auto_scroll(page)

    # 스크롤 후 로딩 대기
    await asyncio.sleep(2)

    # 다시 맨 위로 이동 (정돈된 캡처)
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(1)

    # 전체 페이지 캡처
    await page.screenshot(path=output_path, full_page=True)

    return response
