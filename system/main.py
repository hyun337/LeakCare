import asyncio
import argparse
import httpx
import time
import os
import sys
import cv2
import numpy as np

# 프로젝트 루트를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.utils.report import generate_pdf_report
from system.browser.manager import BrowserManager
from system.core.capture import take_screenshot
from system.core.extractor import (
    extract_metadata,
    get_location,
    extract_images,
    extract_links_with_pagination
)
from system.utils.file_path import generate_evidence_path, get_project_root, get_report_path

# AI 폴더에서 직접 import 
from AI.analyze import Analyze

# BE 서버 주소 — .env로 관리하는 걸 권장
BE_BASE_URL = os.environ.get("BE_BASE_URL", "http://localhost:8000")


# ─────────────────────────────
# [기능 1] 이미지 다운로드
# ─────────────────────────────
async def download_image(url: str):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                return res.content
    except Exception:
        pass
    return None


# ─────────────────────────────
# [기능 2] BE에 결과 PATCH
# ─────────────────────────────
async def update_task_result(task_id: str, evidence_info: dict, ai_detected_results: list, report_path: str = None):
    """
    분석 완료 후 BE에 결과를 PATCH
    """
    update_url = f"{BE_BASE_URL}/api/v1/detection/tasks/{task_id}"

    payload = {
        "status": "completed",
        "metadata": {
            "ip_address": evidence_info["ip"],
            "country": evidence_info["country"],
            "city": evidence_info["city"],
            "collected_at": evidence_info["timestamp"]
        },
        "results": ai_detected_results,
        "screenshot_path": evidence_info["screenshot_path"],
        "report_path": report_path  # PDF 경로 추가
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.patch(update_url, json=payload)
            print(f"📨 [API] 응답: {res.status_code} | {res.text}")
            if res.status_code == 200:
                print(f"✅ [API] Task {task_id} 결과 업데이트 성공")
            else:
                print(f"❌ [API] 업데이트 실패 (HTTP {res.status_code})")
    except Exception as e:
        print(f"⚠️ [API] 서버 연결 실패: {e}")


# ─────────────────────────────
# [기능 3] BE에 실패 PATCH
# ─────────────────────────────
async def notify_failed(task_id: str, error_msg: str):
    """
    분석 실패 시 BE에 failed 상태를 알립니다.
    """
    update_url = f"{BE_BASE_URL}/api/v1/detection/tasks/{task_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.patch(update_url, json={
                "status": "failed",
                "error": error_msg,
                "metadata": None,
                "results": [],
                "screenshot_path": None,
                "report_path": None
            })
            print(f"⚠️ [API] Task {task_id} 실패 상태 전송 완료")
    except Exception as e:
        print(f"⚠️ [API] 실패 상태 전송도 실패: {e}")


# ─────────────────────────────
# [핵심] 분석 로직 (server.py와 공유)
# ─────────────────────────────
async def run_analysis(task_id: str, url: str, mode: str, registered_embeddings: list):
    """
    실제 분석 파이프라인.
    - server.py (FastAPI)에서 호출하거나
    - main() (CLI)에서 직접 호출 모두 가능
    
    registered_embeddings: numpy array 리스트 (BE에서 전달받은 임베딩)
    """
    output_path, filename = generate_evidence_path()

    # AI 분석기 초기화 (한 번만)
    analyzer = Analyze()

    bm = BrowserManager()
    page = await bm.start()

    try:
        # 4. 채증 및 메타데이터 확보
        response = await take_screenshot(page, url, output_path)
        ip = await extract_metadata(response)
        country, city = get_location(ip)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ 채증 성공! | IP: {ip} | 위치: {country}({city})")

        # 5. 이미지 수집
        raw_images = []
        if mode == "single":
            imgs = await extract_images(page)
            raw_images = [(img, url) for img in imgs]
        elif mode == "board":
            linked_pages = await extract_links_with_pagination(page, url, 1, 2)
            for link in linked_pages:
                try:
                    await page.goto(link, wait_until="domcontentloaded", timeout=10000)
                    imgs = await extract_images(page)
                    raw_images.extend([(img, link) for img in imgs])
                except Exception:
                    continue

        # 6. AI 분석 수행
        ai_detected_results = []
        print(f"\n🔍 AI 정밀 분석 시작 (대상: {len(raw_images)}건)...")

        for idx, (img_url, source_page) in enumerate(raw_images):
            img_bytes = await download_image(img_url)
            if not img_bytes:
                continue

            # numpy 배열로 변환
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                continue

            # AI 폴더의 Analyze 사용 (딥페이크 판별 포함)
            result = analyzer.analyze(registered_embeddings, img)

            for r in result.get("results", []):
                status_icon = "🚨 [탐지!]" if r["percent"] >= 50 else "🔍 [분석]"
                print(f"   [{idx+1}/{len(raw_images)}] {status_icon} "
                      f"점수: {r['best_score']:.4f} | "
                      f"딥페이크: {r['is_deepfake']} | "
                      f"위험도: {r['status']} | "
                      f"URL: {img_url[:50]}...")

                # 의심 이상(50%)만 결과에 포함
                if r["percent"] >= 50:
                    ai_detected_results.append({
                        "url": img_url,
                        "score": r["best_score"],
                        "page_url": source_page,
                        "is_deepfake": r["is_deepfake"],
                        "risk_level": r["status"],  # 위험 / 의심 / 안전
                    })

        # 7. PDF 보고서 생성
        evidence_info = {
            "ip": ip,
            "country": country,
            "city": city,
            "timestamp": timestamp,
            "screenshot_path": output_path
        }
        report_full_path = get_report_path(filename)
        generate_pdf_report(evidence_info, ai_detected_results, report_full_path)
        print(f"📄 PDF 보고서 생성: {report_full_path}")

        # 8. BE에 결과 업데이트
        await update_task_result(task_id, evidence_info, ai_detected_results, report_full_path)

    except Exception as e:
        print(f"❌ 엔진 오류 발생: {e}")
        await notify_failed(task_id, str(e))
    finally:
        await bm.stop()


# ─────────────────────────────
# [CLI] 직접 실행 시 (테스트용)
# ─────────────────────────────
async def main():
    parser = argparse.ArgumentParser(description="LeakCare 엔진 (CLI 테스트용)")
    parser.add_argument("url", help="채증할 URL 입력")
    parser.add_argument("--mode", choices=["single", "board"], default="single")
    parser.add_argument("--task_id", required=True, help="백엔드에서 발급한 작업 ID")
    parser.add_argument("--embedding_path", required=True, help="임베딩 JSON 파일 경로")
    parser.add_argument("--video", action="store_true", help="동영상 녹화 활성화")
    args = parser.parse_args()

    # 임베딩 JSON 파일에서 로드
    import json
    if not os.path.exists(args.embedding_path):
        print(f"❌ 임베딩 파일을 찾을 수 없습니다: {args.embedding_path}")
        return

    with open(args.embedding_path) as f:
        data = json.load(f)

    registered_embeddings = [np.array(data["avg_embedding"])]

    await run_analysis(
        task_id=args.task_id,
        url=args.url,
        mode=args.mode,
        registered_embeddings=registered_embeddings
    )


if __name__ == "__main__":
    asyncio.run(main())
