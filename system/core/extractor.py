import asyncio
import requests

def get_location(ip):
    """
    IP 주소를 기반으로 국가/도시 정보 조회
    (외부 API 사용)
    """    
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = res.json()
        if data.get('status') == 'success':
            return data.get('country', 'Unknown'), data.get('city', 'Unknown')
        return "Unknown", "Unknown"
    except:
        return "Unknown", "Unknown"

async def extract_metadata(response):
    """
    Playwright response 객체에서 서버 IP 추출
    """
    server_addr = await response.server_addr()
    ip_address = server_addr.get('ipAddress', 'Unknown IP')
    return ip_address

async def extract_images(page):
    """
    현재 페이지에서 모든 이미지 URL 추출
    """
    images = await page.evaluate("""
        () => {
            const imgs = Array.from(document.querySelectorAll('img'));
            return imgs
                .map(img => img.src) 
                .filter(src => src && src.startsWith('http'));
        }
    """)
    return images

async def extract_links_with_scroll(page, base_url):
    """무한 스크롤하면서 게시물 링크 수집"""
    from urllib.parse import urlparse, parse_qs
    import re

    base_domain = urlparse(base_url).netloc
    
    # 입력 URL에서 게시판 ID 추출 (예: id=w_entertainer)
    base_query = parse_qs(urlparse(base_url).query)
    board_id = base_query.get('id', [None])[0]  # w_entertainer
    
    collected_links = set()
    prev_count = 0
    max_scrolls = 5

    for i in range(max_scrolls):
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a'))
                       .map(a => a.href)
                       .filter(href => href && href.startsWith('http'))
        """)

        for link in links:
            parsed = urlparse(link)
            # 조건 1: 같은 도메인
            if parsed.netloc != base_domain:
                continue
            # 조건 2: 같은 게시판 ID 포함
            if board_id and f'id={board_id}' not in link:
                continue
            # 조건 3: 게시물 URL 패턴 (view 또는 숫자 no= 포함)
            if 'view' in parsed.path or 'no=' in parsed.query:
                collected_links.add(link)
            elif re.search(r'/[A-Za-z0-9]+/\d+$', parsed.path):
                collected_links.add(link)

        print(f"   스크롤 {i+1}/{max_scrolls} | 수집된 게시물: {len(collected_links)}개")

        if len(collected_links) == prev_count:
            print("   더 이상 새 게시물 없음, 종료")
            break
        prev_count = len(collected_links)

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)

    return list(collected_links)

# 핵심 로직!!!
async def extract_links_with_pagination(page, base_url, start_page, end_page):
    """
    게시판 페이지를 순회하면서 게시글 링크 수집
    """
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    import re

    base_domain = urlparse(base_url).netloc

    # 게시판 ID 추출
    base_query = parse_qs(urlparse(base_url).query)
    board_id = base_query.get('id', [None])[0]

    collected_links = []
    seen = set()

    for p in range(start_page, end_page + 1):
        # 페이지 URL 생성
        parsed = urlparse(base_url)
        query = parse_qs(parsed.query)

        # po= 방식이면 po 사용, 아니면 page 사용
        if 'po' in query:
            query['po'] = [str(p - 1)]  # po는 0부터 시작
        else:
            query['page'] = [str(p)]

        new_query = urlencode({k: v[0] for k, v in query.items()})
        page_url = urlunparse(parsed._replace(query=new_query))

        print(f"   📄 {p}페이지 수집 중... ({page_url[:60]})")

        try:
            await page.goto(page_url, wait_until="load", timeout=15000)
            await asyncio.sleep(1)
        except:
            print(f"   ❌ {p}페이지 접속 실패, 스킵")
            continue

        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a'))
                       .map(a => a.href)
                       .filter(href => href && href.startsWith('http'))
        """)

        page_count = 0
        for link in links:
            parsed_link = urlparse(link)

            # 같은 도메인만
            if parsed_link.netloc.replace('www.', '') != base_domain.replace('www.', ''):
                continue

            # 같은 게시판만
            if board_id and f'id={board_id}' not in link:
                continue
            
            # 게스글 패턴 필터링
            is_post = False
            if 'view' in parsed_link.path or 'no=' in parsed_link.query:
                is_post = True
            elif re.search(r'/[A-Za-z0-9]+/\d+$', parsed_link.path):
                is_post = True

            if is_post:
                normalized = link.replace('http://', 'https://')
                if normalized not in seen:
                    seen.add(normalized)
                    collected_links.append(link)
                    page_count += 1

        print(f"   이번 페이지 신규 게시물: {page_count}개 | 누적: {len(collected_links)}개")

    return collected_links
