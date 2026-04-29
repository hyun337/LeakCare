import asyncio
import argparse
import httpx
import time
import os
import sys

# 프로젝트 루트를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.utils.report import generate_pdf_report
from ai_module import analyze_face_bytes, load_target_embedding
from system.browser.manager import BrowserManager
from system.core.capture import take_screenshot
from system.core.extractor import (
    extract_metadata, 
    get_location, 
    extract_images, 
    extract_links_with_pagination
)
from system.utils.file_path import generate_evidence_path, get_project_root, get_report_path

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
        # 다운로드 실패 로그는 간결하게 유지
        pass
    return None

# ─────────────────────────────
# [기능 2] 백엔드 결과 업데이트 함수 (PATCH)
# ─────────────────────────────
async def update_task_result(task_id, evidence_info, ai_detected_results):
    """
    백엔드가 생성한 task_id 기반으로 최종 분석 결과를 DB에 업데이트합니다.
    """
    base_url = "http://localhost:8000" 
    update_url = f"{base_url}/api/v1/detection/tasks/{task_id}"

    payload = {
        "status": "completed",
        "metadata": {
            "ip_address": evidence_info["ip"],
            "country": evidence_info["country"],
            "city": evidence_info["city"],
            "collected_at": evidence_info["timestamp"]
        },
        "results": ai_detected_results,
        "screenshot_path": evidence_info["screenshot_path"]
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.patch(update_url, json=payload, timeout=10.0)
            if res.status_code == 200:
                print(f"✅ [API] Task {task_id} 결과 업데이트 성공")
            else:
                print(f"❌ [API] 업데이트 실패 (HTTP {res.status_code})")
    except Exception:
        print(f"⚠️ [API] 서버 연결 실패 (백엔드가 꺼져 있어도 엔진은 계속 진행됩니다)")

# ─────────────────────────────
# [메인] 시스템 실행 엔진
# ─────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="LeakCare 엔진")
    parser.add_argument("url", help="채증할 URL 입력")
    parser.add_argument("--mode", choices=["single", "board"], default="single")
    parser.add_argument("--task_id", required=True, help="백엔드에서 발급한 작업 ID")
    parser.add_argument("--name", type=str, default="User", help="분석 대상 이름")
    parser.add_argument("--video", action="store_true", help="동영상 녹화 활성화")
    args = parser.parse_args()

    # 1. 경로 설정
    output_path, filename = generate_evidence_path()
    video_dir = os.path.join(get_project_root(), "evidence", "videos")
    
    if args.video and not os.path.exists(video_dir):
        os.makedirs(video_dir)

    # 2. 타겟 사진 로드
    target_photo_path = os.path.join(get_project_root(), "targets", f"{args.name}.jpg")
    if not load_target_embedding(target_photo_path):
        print(f"❌ [AI] 분석 중단: {args.name}.jpg 타겟 사진을 찾을 수 없습니다.")
        return

    # 3. 브라우저 시작
    bm = BrowserManager()
    page = await bm.start(record_video=video_dir if args.video else None)

    try:
        # 4. 채증 및 메타데이터 확보
        response = await take_screenshot(page, args.url, output_path)
        ip = await extract_metadata(response)
        country, city = get_location(ip)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ 채증 성공! | IP: {ip} | 위치: {country}({city})")

        # 5. 이미지 수집
        raw_images = []
        if args.mode == "single":
            imgs = await extract_images(page)
            raw_images = [(img, args.url) for img in imgs]
        elif args.mode == "board":
            linked_pages = await extract_links_with_pagination(page, args.url, 1, 2)
            for link in linked_pages:
                try:
                    await page.goto(link, wait_until="domcontentloaded", timeout=10000)
                    imgs = await extract_images(page)
                    raw_images.extend([(img, link) for img in imgs])
                except: continue

        # 6. AI 분석 수행 (터미널 실시간 로그 추가)
        ai_detected_results = []
        print(f"\n🔍 AI 정밀 분석 시작 (대상: {len(raw_images)}건)...")
        
        for idx, (img_url, source_page) in enumerate(raw_images):
            img_bytes = await download_image(img_url)
            if not img_bytes:
                continue
            
            analysis_res = await analyze_face_bytes(img_bytes)
            score = analysis_res.get("score", 0.0)
            is_match = analysis_res.get("match", False)
            
            # 실시간 유사도 로그 출력
            status_icon = "🚨 [탐지!]" if is_match else "🔍 [분석]"
            print(f"   [{idx+1}/{len(raw_images)}] {status_icon} 점수: {score:.4f} | URL: {img_url[:50]}...")
            
            if is_match:
                ai_detected_results.append({
                    "url": img_url,
                    "score": score,
                    "page_url": source_page
                })

        # 7. 백엔드 업데이트
        evidence_info = {
            "ip": ip, "country": country, "city": city,
            "timestamp": timestamp, "screenshot_path": output_path
        }
        await update_task_result(args.task_id, evidence_info, ai_detected_results)

        # 8. PDF 보고서 생성
        report_full_path = get_report_path(filename)
        generate_pdf_report(evidence_info, ai_detected_results, report_full_path)

    except Exception as e:
        print(f"❌ 엔진 오류 발생: {e}")
    finally:
        await bm.stop()

if __name__ == "__main__":
    asyncio.run(main())
