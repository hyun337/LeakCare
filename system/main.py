import asyncio
import argparse
import httpx
import time
import os
from system.utils.report import generate_pdf_report
from ai_module import analyze_face_bytes

from system.browser.manager import BrowserManager
from system.core.capture import take_screenshot
from system.core.extractor import (
    extract_metadata, 
    get_location, 
    extract_images, 
    extract_links_with_pagination
)
from system.utils.file_path import generate_evidence_path

# ─────────────────────────────
# [기능 1] 이미지 다운로드 함수
# ─────────────────────────────
async def download_image(url):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                return res.content
    except Exception as e:
        print(f"⚠️  [이미지 다운로드 실패] {url[:50]}... | 오류: {e}")
    return None

# ─────────────────────────────
# [기능 2] 백엔드 API 연동 함수
# ─────────────────────────────
async def send_to_backend(target_url, name, evidence_info):
    base_url =  ""
    analyze_url = f"{base_url}/api/v1/detection/analyze"
    metadata_url = f"{base_url}/api/v1/detection/metadata"
    login_url = f"{base_url}/api/v1/users/login"

    max_retries = 3 # 최대 재시도 횟수
    retry_delay = 2 # 재시도 간격 (초)
    
    for attempt in range(max_retries):
        async with httpx.AsyncClient() as client:
            try:
                # 1) 로그인
                login_res = await client.post(login_url, data={
                    "username": "str@example.com",
                    "password": "string"
                }, timeout=10.0)
                
                if login_res.status_code != 200:
                    print(f"❌ [API] 로그인 실패 (HTTP {login_res.status_code})")
                    
                token = login_res.json().get("access_token")
                if not token:
                    print("❌ [API] 토큰 없음")

                # 2) 분석 요청
                headers = {"Authorization": f"Bearer {token}"}
                analyze_payload = {"url": target_url, "target_name": name}
                res_analyze = await client.post(
                    analyze_url, json=analyze_payload,
                    headers=headers, timeout=10.0
                )
                
                if res_analyze.status_code != 200:
                    print(f"❌ [API] analyze 실패 (HTTP {res_analyze.status_code})")

                task_id = res_analyze.json().get("task_id")
                if not task_id:
                    print("❌ [API] task_id 없음 (analyze 응답 이상)")

                # 3) 메타데이터 전송
                metadata_payload = {
                    "task_id": task_id, 
                    "ip_address": evidence_info["ip"],
                    "country": evidence_info["country"],
                    "city": evidence_info["city"],
                    "screenshot_path": evidence_info["screenshot_path"],
                    "video_path": evidence_info.get("video_path", ""),
                    "target_url": target_url,
                    "collected_at": evidence_info["timestamp"]
                }
                res_meta = await client.post(
                    metadata_url, json=metadata_payload,
                    headers=headers, timeout=10.0
                )
                if res_meta.status_code not in [200, 201]:
                    print(f"⚠️  [API] metadata 전송 실패: HTTP {res_meta.status_code} ")

                # 모든 과정 성공 시 task_id 반환하고 종료
                return task_id

            except (httpx.ConnectError, httpx.TimeoutException, Exception) as e:
                # repr(e) 사용 - 에러 클래스명까지 출력
                error_msg = repr(e) if not str(e) else str(e)
                print(f"⚠️ [API 연동 시도 {attempt + 1}/{max_retries}] 실패 원인: {error_msg}")
                
                if attempt < max_retries - 1:
                    # 마지막 시도가 아니면 지정된 시간만큼 대기 후 재시도
                        await asyncio.sleep(retry_delay)
                else:
                    # 모든 시도가 실패했을 때
                    print(f"❌ [API] 최종 연동 실패 (네트워크 또는 서버 오류)")
                    return None
            
# ─────────────────────────────
# [기능 3] 개별 페이지 이미지 수집
# ─────────────────────────────
async def collect_images_from_page(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        return await extract_images(page)
    except Exception as e:
        print(f"⚠️  [페이지 수집 실패] {url[:50]}... | 오류: {e}")
        return []

# ─────────────────────────────
# [헬퍼] raw_images 정규화
# ─────────────────────────────
def normalize_images(imgs, fallback_url):
    """
    extract_images 반환값이 tuple 리스트일 수도, 문자열 리스트일 수도 있어서
    항상 (img_url, source_page) 형태로 통일
    """
    if not imgs:
        return []
    if isinstance(imgs[0], tuple):
        return [(img_url, fallback_url) for img_url, *_ in imgs]
    return [(img, fallback_url) for img in imgs]

# ─────────────────────────────
# [메인] 시스템 실행 엔진
# ─────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="LeakCare 엔진")
    parser.add_argument("url", help="채증할 URL 입력")
    parser.add_argument("--mode", choices=["single", "board"], default="single")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=5)
    parser.add_argument("--video", action="store_true", help="동영상 녹화 활성화")
    parser.add_argument("--name", type=str, default="Unknown", help="분석 대상 이름")
    args = parser.parse_args()

    current_dir = os.getcwd()
    output_path, filename = generate_evidence_path()
    video_dir = os.path.join(current_dir, "evidence/videos")
    
    if args.video and not os.path.exists(video_dir):
        os.makedirs(video_dir)

    bm = BrowserManager()
    page = await bm.start(record_video=video_dir if args.video else None)

    try:
        # ── 1. 초기 채증 및 메타데이터 확보 ──────────────────────────
        response = await take_screenshot(page, args.url, output_path)
        ip = await extract_metadata(response)
        country, city = get_location(ip)
        print(f"✅ 채증 성공! | IP: {ip} | 위치: {country}({city})")

        # ── 2. 이미지 수집 ────────────────────────────────────────────
        raw_images = []
        if args.mode == "single":
            try:
                imgs = await extract_images(page)
                raw_images.extend(normalize_images(imgs, args.url))
            except Exception as e:
                print(f"❌ [이미지 수집 오류] single 모드: {e}")

        elif args.mode == "board":
            try:
                linked_pages = await extract_links_with_pagination(
                    page, args.url, args.start, args.end
                )
                for idx, link in enumerate(linked_pages):
                    print(f"   [{idx+1}/{len(linked_pages)}] 게시글 탐색 중...", end="\r")
                    imgs = await collect_images_from_page(page, link)
                    raw_images.extend(normalize_images(imgs, link))
            except Exception as e:
                print(f"❌ [이미지 수집 오류] board 모드: {e}")

        # ── 3. 필터링 ─────────────────────────────────────────────────
        exclude_keywords = [
            "google", "gstatic", "ad-", "banner",
            "logo", "favicon", "reply", ".gif"
        ]
        all_images = [
            img for img in list(set(raw_images))
            if not any(key in img[0].lower() for key in exclude_keywords)
        ]

        # ★ 이미지가 없으면 API 연동 자체를 시도하지 않으므로 명시적으로 알림
        if not all_images:
            print("\n⚠️  수집된 이미지가 없습니다. API 연동을 건너뜁니다.")
            print("   (페이지 구조 확인 또는 --mode 옵션을 점검하세요)")
            # 빈 결과로 보고서만 생성
            report_filename = filename.replace(".png", "_report.pdf")
            generate_pdf_report({
                "target_url": args.url, "ip": ip,
                "location": f"{country}({city})",
                "screenshot_path": os.path.join(current_dir, filename)
            }, [], os.path.join(current_dir, report_filename))
            
            return

        # ── 4. AI 분석 + API 연동 ─────────────────────────────────────
        print(f"\n🔍 AI 정밀 분석 시작 (대상: {len(all_images)}건)...")
        start_time = time.time()

        ai_detected_results = []
        api_success_count = 0
        api_fail_count = 0
        api_skip_count = 0   # 이미지 다운로드 실패로 API 호출 못 한 경우

        for idx, (img_url, source_page) in enumerate(all_images):
            print(f"     [{idx+1}/{len(all_images)}] 이미지 분석 중...", end="\r")

            img_bytes = await download_image(img_url)
            if not img_bytes:
                api_skip_count += 1
                continue
            
            analysis_res = await analyze_face_bytes(img_bytes)
            score = analysis_res.get("score", 0.0)
            print(f"     [결과 {idx+1}] 점수: {score:.4f} | URL: {img_url[:50]}...")

            # 임계값 0.60 이상 매칭된 경우만 실행
            if analysis_res.get("match"): 
                match_score = score
                face_filename = f"match_{idx}_{filename}"
                face_path = os.path.join(current_dir, face_filename)
               
                with open(face_path, "wb") as f:
                    f.write(img_bytes)

                    # 유출 리스트에 추가    
                    ai_detected_results.append({
                        "url": img_url,
                        "score": match_score,
                        "page_url": source_page,
                        "local_path": face_path
                    })
            
                # API 전송용 데이터 구성
                video_path = ""
                if args.video and page.video:
                    try: video_path = await page.video.path()
                    except : pass

                current_evidence = {
                    "ip": ip, "country": country, "city": city,
                    "screenshot_path": face_path, # 전체 스크린샷 대신 매칭된 사진 전송
                    "video_path": video_path,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # 여기서만 API 호출
                task_id = await send_to_backend(source_page, args.name, current_evidence)
                if task_id:
                    api_success_count += 1
                else:
                    api_fail_count += 1

            else:
                # 점수가 0.60 미만이면 아무것도 하지 않고 스킵 카운트만 올림
                api_skip_count += 1

            await asyncio.sleep(0.5)

        # ── 5. 결과 요약 출력 ─────────────────────────────────────────
        elapsed = int(time.time() - start_time)
        print()  # 줄바꿈 (end="\r" 후 정리)

        total_attempted = api_success_count + api_fail_count
        if total_attempted == 0:
            # API 연동을 한 번도 시도 못 한 경우 (전부 다운로드 실패 등)
            print(f"⚠️  분석 완료, API 연동 시도 없음! (이미지 다운로드 전체 실패, 소요 시간: {elapsed}초)")
        elif api_fail_count == 0:
            print(f"✅ 분석 및 API 연동 완료! (소요 시간: {elapsed}초)")
        elif api_success_count == 0:
            print(f"❌ 분석 완료, API 연동 전체 실패! (소요 시간: {elapsed}초)")
        else:
            print(
                f"⚠️  분석 완료, API 연동 일부 실패! "
                f"성공: {api_success_count}건 / 실패: {api_fail_count}건 "
                f"(소요 시간: {elapsed}초)"
            )

        if api_skip_count > 0:
            print(f"   ℹ️  임계값 미달 또는 다운로드 실패로 제외된 항목: {api_skip_count}건")

        print("-" * 50)
        if ai_detected_results:
            print(f"🚨 [경고] 유출 의심 콘텐츠가 {len(ai_detected_results)}건 탐지되었습니다!")
            for res in ai_detected_results:
                print(f"   📍 유사도: {res['score']:.4f} | 출처: {res['page_url'][:50]}...")
        else:
            print("✅ 분석 결과, 등록된 얼굴과 일치하는 유출물이 없습니다.")
        print("-" * 50)

        # ── 6. 보고서 생성 ────────────────────────────────────────────
        report_filename = filename.replace(".png", "_report.pdf")
        generate_pdf_report({
            "target_url": args.url, "ip": ip,
            "location": f"{country}({city})",
            "screenshot_path": os.path.join(current_dir, filename)
        }, ai_detected_results, os.path.join(current_dir, report_filename))
        

    except Exception as e:
        print(f"❌ 엔진 오류: {e}")
    finally:
        await bm.stop()

if __name__ == "__main__":
    asyncio.run(main())
