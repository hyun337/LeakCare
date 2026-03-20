import asyncio

async def auto_scroll(page):
    """페이지 하단까지 스크롤하여 지연 로딩 콘텐츠를 활성화합니다."""
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                let distance = 300; 
                let timer = setInterval(() => {
                    let scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if(totalHeight >= scrollHeight){
                        clearInterval(timer);
                        resolve();
                    }
                }, 200);
            });
        }
    """)

async def take_screenshot(page, url, output_path):
    print(f"🌐 {url} 접속 중...")
    
    response = await page.goto(url, wait_until="load") 
    
    # [추가] 자동 스크롤 실행
    await auto_scroll(page)
    await asyncio.sleep(2) # 스크롤 후 최종 로딩 대기
    
    # [추가] 맨 위로 올라와서 정돈된 상태로 캡처
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(1)
    
    await page.screenshot(path=output_path, full_page=True)
    return response
