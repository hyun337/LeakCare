import asyncio
import random

async def auto_scroll(page):
    """
    사람이 직접 마우스 휠을 내리는 것처럼 불규칙하게 스크롤
    (봇 탐지 우회 핵심 로직)
    """
    print("🖱️ [엔진] 정밀 스크롤을 시작합니다...")
    
    # 총 스크롤 횟수 설정 (페이지 길이에 따라 5~10회 사이 랜덤)
    scroll_times = random.randint(5, 10)
    
    for i in range(scroll_times):
        # 1. 스크롤 거리 랜덤 설정 
        distance = random.randint(300, 700)
        
        # 2. 마우스 휠 동작 모사 (기계적 scrollBy 대신 mouse.wheel 사용)
        await page.mouse.wheel(0, distance)
        
        # 3. 사람처럼 콘텐츠를 읽는 시간 시뮬레이션 (0.5~1.5초 무작위 대기)
        wait_time = random.uniform(0.5, 1.5)
        await asyncio.sleep(wait_time)
        
        # 중간에 바닥에 도달했는지 체크
        is_bottom = await page.evaluate("""
            () => (window.innerHeight + window.scrollY) >= document.body.scrollHeight
        """)
        if is_bottom:
            break

async def click_more_buttons(page):
    """
    버튼 클릭 전 마우스를 버튼 위로 이동시키는 '호버(Hover)' 동작 추가
    """
    more_selectors = [
        "button:has-text('더보기')", 
        "button:has-text('결과 더보기')", # 구글 전용 추가
        "a:has-text('더보기')", 
        "button:has-text('More')", 
        ".btn-more", 
        "#load-more",
        ".mye4qd" # 구글 이미지 '결과 더보기' 클래스
    ]
    
    click_count = 0
    max_clicks = 3

    for selector in more_selectors:
        if click_count >= max_clicks:
            break
            
        try:
            button = await page.query_selector(selector)
            if button and await button.is_visible():
                # 바로 클릭하지 않고 마우스를 버튼 위로 이동 (호버 효과)
                await button.hover()
                await asyncio.sleep(random.uniform(0.5, 1.0))
                
                print(f"👆 [엔진] '{selector}' 버튼 발견, 클릭 시뮬레이션 중...")
                await button.click()
                click_count += 1
                
                # 로딩 대기 후 추가 스크롤
                await asyncio.sleep(2)
                await auto_scroll(page) 
        except:
            continue

async def take_screenshot(page, url, output_path):
    print(f"🌐 {url} 접속 중...")

    # 1. 페이지 접속 (타임아웃 여유 있게 설정)
    response = await page.goto(url, wait_until="networkidle", timeout=60000)

    # 2. 정밀 스크롤 (봇 탐지 회피용)
    await auto_scroll(page)

    # 3. 더보기 버튼 탐색 및 클릭
    await click_more_buttons(page)

    # 4. 최종 캡처 전 인간적인 대기 시간
    await asyncio.sleep(random.uniform(1.0, 2.0))
    await page.evaluate("window.scrollTo(0, 0)")
    
    await page.screenshot(path=output_path, full_page=True)
    return response
