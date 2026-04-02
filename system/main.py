import asyncio
import argparse
import httpx
import ai_module
import time
import os
from system.utils.report import generate_pdf_report

# 시스템 내부 모듈 임포트
from system.browser.manager import BrowserManager
from system.core.capture import take_screenshot
from system.core.extractor import (
    extract_metadata, 
    get_location, 
    extract_images, 
    extract_links_with_pagination
)
from system.utils.file_path import (
    generate_evidence_path
)

# ─────────────────────────────
# [기능 1] 이미지 다운로드 함수
# ─────────────────────────────
async def download_image(url):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                return res.content
    except:
        pass
    return None

# ─────────────────────────────
# [기능 2] 백엔드 API 연동 함수 
# ─────────────────────────────
async def send_to_backend(target_url, name, evidence_info):
    # 백엔드 서버로 분석 요청 및 메타데이터 전송
    base_url = "https://5528-121-67-233-19.ngrok-free.app"
    analyze_url = f"{base_url}/api/v1/detection/analyze"
    metadata_url = f"{base_url}/api/v1/detection/metadata"
    
    async with httpx.AsyncClient() as client:
        try:
            # 1단계: 분석 요청
            analyze_payload = {"url": target_url, "target_name": name}
            res_analyze = await client.post(analyze_url, json=analyze_payload, timeout=10.0)
            
            if res_analyze.status_code == 200:
                task_id = res_analyze.json().get('task_id')
                print(f"✅ [API] 분석 요청 성공! (Task ID: {task_id})")
                
                # 2단계: 메타데이터 전송
                metadata_payload = {
                    "task_id": task_id, # BE 추가 예정 !!!!!!!!!!!!!!!!!!!!!!
                    "ip_address": evidence_info['ip'],
                    "country": evidence_info['country'],
                    "city": evidence_info['city'],
                    "screenshot_path": evidence_info['screenshot_path'],
                    "target_url": target_url,
                    "collected_at": evidence_info['timestamp']
                }
                res_meta = await client.post(metadata_url, json=metadata_payload, timeout=10.0)

                if res_meta.status_code in [200, 201]:
                    print(f"☑️ [API] DB 메타데이터 저장 완료! (IP: {evidence_info['ip']})")
                else:
                    print(f"⚠️ [API] 메타데이터 저장 실패: {res_meta.status_code}")
                return task_id
            else:
                print(f"❌ [API] 분석 요청 실패: {res_analyze.status_code}")
        except Exception as e:
            print(f"❌ [API] 연동 중 오류 발생: {e}")
    return None

# ─────────────────────────────
# [기능 3] 개별 페이지 이미지 수집
# ─────────────────────────────
async def collect_images_from_page(page, url):
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)
        images = await extract_images(page)
        return images
    except:
        return []

# ─────────────────────────────
# [메인] 시스템 실행 엔진
# ─────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="LeakCare 엔진")
    parser.add_argument("url", help="채증할 URL 입력")
    parser.add_argument("--mode", choices=["single", "board"], default="single")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=5)
    args = parser.parse_args()

    bm = BrowserManager()
    page = await bm.start()

    try:
        # 1. 사이트 접속 및 증거 채증 (메타데이터 확보)
        output_path, filename = generate_evidence_path()
        response = await take_screenshot(page, args.url, output_path)
        
        ip = await extract_metadata(response)
        country, city = get_location(ip)
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        current_dir = os.getcwd()

        print(f"✅ 채증 성공! | IP: {ip} | 위치: {country}({city})")

        raw_images = []

        # 2. 모드별 이미지 수집 (튜플 구조 유지)
        if args.mode == "single":
            print(f"\n🗂️ 단일 페이지 이미지 수집 중...")
            imgs = await extract_images(page)
            raw_images.extend([(img_url, args.url) for img_url, src in imgs] if isinstance(imgs[0], tuple) else [(img, args.url) for img in imgs])

        elif args.mode == "board":
            linked_pages = await extract_links_with_pagination(page, args.url, args.start, args.end)
            print(f"\n🗂️ 이미지 수집 시작 (총 {len(linked_pages)}개 게시물)")
            for idx, link in enumerate(linked_pages):
                print(f"   [{idx+1}/{len(linked_pages)}] 게시글 탐색 중...", end="\r")
                imgs = await collect_images_from_page(page, link)
                raw_images.extend([(img, link) for img in imgs])
            print("\n✅ 모든 게시물 탐색 완료!")

        # 3. 분석 대상 필터링
        exclude_keywords = ["google", "gstatic", "ad-", "banner", "logo", "favicon", "reply", ".gif"]
        unique_images = list(set(raw_images)) 
        all_images = [
            img for img in unique_images 
            if not any(key in img[0].lower() for key in exclude_keywords)
        ]

        # 4. AI 분석 실행
        matched = []
        start_time = time.time()
        print(f"🔍 AI 분석 시작 (대상: {len(all_images)}건)...")

        for idx, (img_url, source_page) in enumerate(all_images):
            img_data = await download_image(img_url)
            if img_data and len(img_data) > 10240:
                analysis = await ai_module.analyze_face(img_data)
                results = analysis.get('results', [])
                
                # 분석 결과가 있든 없든 조사한 게시물의 메타데이터를 즉시 전송
                current_evidence = {
                    "ip": ip, "country": country, "city": city,
                    "screenshot_path": os.path.join(current_dir, filename),
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "img_url": img_url # 개별 이미지 URL 추가
                }
                # 실시간 동기화 호출
                await send_to_backend(source_page, "이서현", current_evidence)

                for face in results:
                    score = face.get('score', 0)
                    if score >= 0.85:
                        print(f"   ⚠️ 유출 의심 발견! [{idx+1}] 점수: {score}...")
                        matched.append({"url": img_url, "page": source_page, "score": score})
        end_time = time.time()
        print("-" * 50)
        print(f"✅ 분석 완료! (소요 시간: {int(end_time - start_time)}초)")
        print(f"🚨 총 {len(matched)}건의 유출 의심 사례를 발견했습니다.")

        # 5. 백엔드 연동 (수집된 메타데이터 포함하여 호출) 
        evidence_info = {
            "ip": ip,
            "country": country,
            "city": city,
            "screenshot_path": os.path.join(current_dir, filename),
            "timestamp": current_time
        }
        await send_to_backend(args.url, "이서현", evidence_info)

        # 6. PDF 보고서 생성
        report_filename = filename.replace(".png", "_report.pdf")
        pdf_save_path = os.path.join(current_dir, report_filename)
        
        report_data = {
            "target_url": args.url, "ip": ip, "location": f"{country}({city})",
            "screenshot_path": evidence_info['screenshot_path']
        }
        generate_pdf_report(report_data, matched, pdf_save_path)

    except Exception as e:
        print(f"❌ 엔진 오류 발생: {e}")
    finally:
        await bm.stop() 

if __name__ == "__main__":
    asyncio.run(main())


