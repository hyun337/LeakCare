import asyncio
import random


async def auto_scroll(page):
    """
    빠른 스크롤 - 횟수와 대기 시간 축소
    """
    scroll_times = random.randint(2, 4)  

    for i in range(scroll_times):
        distance = random.randint(400, 800)
        await page.mouse.wheel(0, distance)
        await asyncio.sleep(random.uniform(0.2, 0.5)) 

        is_bottom = await page.evaluate("""
            () => (window.innerHeight + window.scrollY) >= document.body.scrollHeight
        """)
        if is_bottom:
            break


async def click_more_buttons(page):
    """
    더보기 버튼 클릭 - 대기 시간 축소
    """
    more_selectors = [
        "button:has-text('더보기')",
        "button:has-text('결과 더보기')",
        "a:has-text('더보기')",
        "button:has-text('More')",
        ".btn-more",
        "#load-more",
        ".mye4qd"
    ]

    click_count = 0
    max_clicks = 2  

    for selector in more_selectors:
        if click_count >= max_clicks:
            break

        try:
            button = await page.query_selector(selector)
            if button and await button.is_visible():
                await button.hover()
                await asyncio.sleep(0.3)  

                await button.click()
                click_count += 1

                await asyncio.sleep(1)  
                await auto_scroll(page)
        except:
            continue


async def take_screenshot(page, url, output_path):
    print(f"🌐 {url} 접속 중...")

    response = await page.goto(url, wait_until="load", timeout=30000)
    
    try:
        await page.wait_for_selector("body", state="attached", timeout=5000)
        
    except Exception:
        print(" [경고] 특정 엘리먼트 대기 타임아웃, 기본 지연 시간 체제로 전환합니다.")
    
    await asyncio.sleep(2.0)
    
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await asyncio.sleep(0.3)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(0.3)
    
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(0.2)
    
    await page.screenshot(path=output_path, full_page=True)
    return response
