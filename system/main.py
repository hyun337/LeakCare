import asyncio
import argparse
import httpx
import time
import os
import sys
import cv2
import numpy as np

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
from AI.analyze import Analyze

BE_BASE_URL = os.environ.get("BE_BASE_URL", "https://d60e-121-67-233-19.ngrok-free.app")
SYSTEM_BASE_URL = os.environ.get("SYSTEM_BASE_URL", "https://aloof-absurd-altitude.ngrok-free.dev")


async def download_image(url: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url)
            if res.status_code == 200:
                return res.content
    except Exception:
        pass
    return None


async def update_task_result(task_id: str, evidence_info: dict, ai_detected_results: list, report_path: str = None):
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
        "report_path": report_path
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.patch(update_url, json=payload)
            print(f"📨 [API] 응답: {res.status_code} | {res.text}")
            if res.status_code == 200:
                print(f"✅ [API] Task {task_id} 결과 업데이트 성공")
            else:
                print(f"❌ [API] 업데이트 실패 (HTTP {res.status_code})")
    except Exception as e:
        print(f"⚠️ [API] 서버 연결 실패: {e}")


async def notify_failed(task_id: str, error_msg: str):
    update_url = f"{BE_BASE_URL}/api/v1/detection/tasks/{task_id}"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            await client.patch(update_url, json={
                "status": "failed",
                "metadata": {
                    "ip_address": "0.0.0.0",
                    "country": "Unknown",
                    "city": "Unknown",
                    "collected_at": "1970-01-01T00:00:00"
                },
                "results": [],
                "screenshot_path": None,
                "report_path": None
            })
            print(f"⚠️ [API] Task {task_id} 실패 상태 전송 완료")
    except Exception as e:
        print(f"⚠️ [API] 실패 상태 전송도 실패: {e}")


async def fetch_task_details(task_id: str):
    detail_url = f"{BE_BASE_URL}/api/v1/detection/tasks/{task_id}/details"
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(detail_url)
        if res.status_code != 200:
            raise Exception(f"task 정보 조회 실패 (HTTP {res.status_code}): {res.text}")
        return res.json()


async def run_analysis_by_task_id(task_id: str):
    try:
        details = await fetch_task_details(task_id)
        url = details.get("url")
        mode = details.get("mode", "single")
        embedding = details.get("target_embedding")

        if not embedding:
            await notify_failed(task_id, "등록된 얼굴 데이터가 없습니다. 먼저 얼굴 사진을 등록해 주세요.")
            return
        if not url:
            await notify_failed(task_id, "분석할 URL 정보가 없습니다.")
            return

        registered_embeddings = [np.array(embedding)]
        await run_analysis(task_id, url, mode, registered_embeddings)

    except Exception as e:
        print(f"❌ run_analysis_by_task_id 오류: {e}")
        await notify_failed(task_id, str(e))


async def run_analysis(task_id: str, url: str, mode: str, registered_embeddings: list):
    output_path, filename = generate_evidence_path()
    analyzer = Analyze()
    bm = BrowserManager()
    page = await bm.start()

    # 썸네일 저장 디렉토리 준비
    thumbnail_dir = os.path.join(get_project_root(), "evidence", "thumbnails")
    os.makedirs(thumbnail_dir, exist_ok=True)

    try:
        response = await take_screenshot(page, url, output_path)
        ip = await extract_metadata(response)
        country, city = get_location(ip)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"✅ 채증 성공! | IP: {ip} | 위치: {country}({city})")

        raw_images = []
        if mode == "single":
            imgs = await extract_images(page)
            raw_images = [(img, url) for img in imgs]
        elif mode == "board":
            linked_pages = await extract_links_with_pagination(page, url, 1, 2)
            for link in linked_pages:
                try:
                    await page.goto(link, wait_until="domcontentloaded", timeout=30000)
                    imgs = await extract_images(page)
                    raw_images.extend([(img, link) for img in imgs])
                except Exception as e:
                    print(f"⚠️ 링크 접근 실패, 스킵: {link[:50]} | {e}")
                    continue

        ai_detected_results = []
        print(f"\n🔍 AI 정밀 분석 시작 (대상: {len(raw_images)}건)...")

        for idx, (img_url, source_page) in enumerate(raw_images):
            img_bytes = await download_image(img_url)
            if not img_bytes:
                continue
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                continue

            result = analyzer.analyze(registered_embeddings, img)
            for r in result.get("results", []):
                if r["percent"] >= 50:
                    # 탐지된 이미지 로컬 저장
                    thumb_filename = f"{filename.replace('.png', '')}_{idx}.jpg"
                    thumb_path = os.path.join(thumbnail_dir, thumb_filename)
                    cv2.imwrite(thumb_path, img)

                    print(f"   🚨 [탐지!][{idx+1}/{len(raw_images)}] "
                          f"점수: {r['best_score']:.4f} | "
                          f"딥페이크: {r['is_deepfake']} | "
                          f"위험도: {r['status']} | "
                          f"URL: {img_url[:50]}...")

                    ai_detected_results.append({
                        "url": img_url,
                        "page_url": source_page,
                        "score": r["best_score"],
                        "matched": r["percent"] >= 50,
                        "is_deepfake": r["is_deepfake"],
                        "risk_level": r["status"],
                        "thumbnail_local_path": thumb_path,
                        "reason": f"유사도 {r['percent']}% - {'딥페이크 감지됨' if r['is_deepfake'] else '얼굴 일치'}",
                    })

        evidence_info = {
            "ip": ip,
            "country": country,
            "city": city,
            "timestamp": timestamp,
            "screenshot_path": output_path,
            "target_url": url,
            "location": f"{country}({city})"
        }

        report_full_path = get_report_path(filename)
        generate_pdf_report(evidence_info, ai_detected_results, report_full_path)
        print(f"📄 PDF 보고서 생성: {report_full_path}")

        report_filename = os.path.basename(report_full_path)
        report_url = f"{SYSTEM_BASE_URL}/reports/{report_filename}"

        await update_task_result(task_id, evidence_info, ai_detected_results, report_url)

    except Exception as e:
        print(f"❌ 엔진 오류 발생: {e}")
        await notify_failed(task_id, str(e))
    finally:
        await bm.stop()


async def main():
    parser = argparse.ArgumentParser(description="LeakCare 엔진 (CLI 테스트용)")
    parser.add_argument("url", help="채증할 URL 입력")
    parser.add_argument("--mode", choices=["single", "board"], default="single")
    parser.add_argument("--task_id", required=True, help="백엔드에서 발급한 작업 ID")
    parser.add_argument("--embedding_path", required=True, help="임베딩 JSON 파일 경로")
    parser.add_argument("--video", action="store_true", help="동영상 녹화 활성화")
    args = parser.parse_args()

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
