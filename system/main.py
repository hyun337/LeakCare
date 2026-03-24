import asyncio
import argparse
import httpx

# 브라우저 실행/종료 관리
from system.browser.manager import BrowserManager

# 페이지 캡처 관련
from system.core.capture import take_screenshot

# 데이터 추출 관련
from system.core.extractor import (
    extract_metadata,      # IP 추출
    get_location,          # IP → 위치 변환
    extract_images,        # 이미지 URL 추출
    extract_links_with_pagination  # 게시판 링크 수집
)

# 파일/진행상태 관리
from system.utils.file_path import (
    generate_evidence_path,
    save_progress,
    load_progress,
    delete_progress
)

# 이미지 다운로드 함수
async def download_image(url):
    """
    이미지 URL을 받아 실제 이미지 데이터를 다운로드
    """
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            res = await client.get(url)
            if res.status_code == 200:
                return res.content  # 이미지 binary 데이터 반환
    except:
        pass
    return None


async def collect_images_from_page(page, url):
    """
    특정 게시글 페이지에 접속해서 이미지들을 추출
    """
    try:
        # 페이지 이동 (DOM 로딩까지만 기다림 → 속도 최적화)
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)

        # 이미지 URL 추출
        images = await extract_images(page)
        return images
    except:
        return []


async def main():
    """
    프로그램 전체 실행 흐름
    """

    # ─────────────────────────────
    # 1. 실행 옵션 설정 (CLI 입력)
    # ─────────────────────────────
    parser = argparse.ArgumentParser(description="LeakCare 엔진")

    parser.add_argument("url", help="채증할 URL 입력")

    parser.add_argument(
        "--mode",
        choices=["single", "board"],
        default="single",
        help="single: 단일 페이지 | board: 게시판"
    )

    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=5)

    parser.add_argument("--resume", action="store_true")

    args = parser.parse_args()

    # ─────────────────────────────
    # 2. 브라우저 실행
    # ─────────────────────────────
    bm = BrowserManager()
    page = await bm.start()

    try:
        # ─────────────────────────────
        # 3. 페이지 캡처 + IP 추출
        # ─────────────────────────────
        output_path, filename = generate_evidence_path()

        # 스크린샷 찍기
        response = await take_screenshot(page, args.url, output_path)

        # 서버 IP 추출
        ip = await extract_metadata(response)

        # IP → 국가/도시 변환
        country, city = get_location(ip)

        print(f"✅ 채증 성공! | IP: {ip} | 위치: {country}({city})")
        print(f"📂 저장파일명: {filename}")

        all_images = []

        # ─────────────────────────────
        # 4. single 모드 (단일 페이지)
        # ─────────────────────────────
        if args.mode == "single":
            print(f"\n🖼 단일 페이지 이미지 수집 중...")

            imgs = await extract_images(page)

            # (이미지URL, 출처페이지) 형태로 저장
            all_images.extend([(img, args.url) for img in imgs])

            print(f"   수집된 이미지: {len(imgs)}개")

        # ─────────────────────────────
        # 5. board 모드 (게시판 크롤링)
        # ─────────────────────────────
        elif args.mode == "board":

            start_index = 0
            linked_pages = []

            # ── 이어서 실행 옵션 ──
            if args.resume:
                progress, prog_file = load_progress(args.url, args.start, args.end)

                if progress:
                    linked_pages = progress["linked_pages"]
                    start_index = progress["last_index"] + 1

                    print(f"🔄 이어서 실행 | {start_index}번째부터")
                else:
                    print("⚠ 저장된 진행 상태 없음")

            # ── 처음 실행이면 링크 수집 ──
            if not args.resume or not linked_pages:
                print(f"\n🔗 링크 수집 중...")

                linked_pages = await extract_links_with_pagination(
                    page, args.url, args.start, args.end
                )

                print(f"총 게시물: {len(linked_pages)}개")
                start_index = 0

            # ── 게시글 순회하면서 이미지 수집 ──
            print(f"\n🖼 이미지 수집 시작")

            for idx in range(start_index, len(linked_pages)):
                link = linked_pages[idx]

                print(f"[{idx+1}] {link[:60]}...")

                imgs = await collect_images_from_page(page, link)

                all_images.extend([(img, link) for img in imgs])

                # 안전장치 (과도한 수집 방지)
                if len(all_images) > 500:
                    print("⚠ 500개 초과 → 중단")

                    save_progress(
                        linked_pages, idx,
                        args.url, args.start, args.end
                    )
                    break
            else:
                # 정상 완료 시 진행 상태 삭제
                delete_progress(args.url, args.start, args.end)
                print("✅ 전체 완료")

        print(f"\n🖼 총 이미지: {len(all_images)}개")

        # ─────────────────────────────
        # 6. AI 분석 (현재 TODO)
        # ─────────────────────────────
        matched = []

        for idx, (img_url, source_page) in enumerate(all_images):
            img_data = await download_image(img_url)

            if img_data is None:
                continue

            # TODO: 얼굴 유사도 분석
            # similarity = ai_module.compare(...)
            # if similarity >= 0.85:
            #     matched.append(...)

        print("-" * 40)
        print(f"🔍 매칭 결과: {len(matched)}개")
        print("-" * 40)

    except Exception as e:
        print(f"❌ 오류: {e}")

    finally:
        # 브라우저 종료 (메모리 누수 방지)
        await bm.stop()


# 프로그램 시작점
if __name__ == "__main__":
    asyncio.run(main())
