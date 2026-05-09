from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import List, Optional
from app.schemas.metadata import MetadataCreate 
from app.schemas.detection import DetectionRequest, DetectionResponse, DetectionDetailResponse, TaskUpdateRequest
from app.core.database import db_instance
import uuid
import asyncio
import random
import subprocess
import os
import sys 
import httpx
from datetime import datetime
from app.api.v1.dependencies import get_current_user
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from app.services.selector import get_system_mode

router = APIRouter()

# 가상 AI 분석 로직
async def run_analysis_and_update(task_id: str, url: str):
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage", # 공유 메모리 사용 안함 (메모리 절약)
                    "--disable-gpu",           # GPU 가속 끔 (서버 환경 필수)
                    "--single-process",        # 프로세스를 하나로 통합 (가장 중요)
                    "--js-flags='--max-old-space-size=128'" # JS 엔진 메모리 제한
                ]
            )
            context = await browser.new_context()
            page = await context.new_page()
            
            # 리소스를 많이 잡아먹는 이미지, 폰트 로딩 차단
            await page.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2}", lambda route: route.abort())

            # 접속 시도 (타임아웃 짧게)
            await page.goto(url, timeout=15000, wait_until="commit")
            
            title = await page.title()
            result_data = {"status": "completed", "title": title}
            
    except Exception as e:
        result_data = {"status": "failed", "error": f"Resource Limit or Error: {repr(e)}"}
    finally:
        if browser:
            await browser.close()


# 에러 기록용 공통 함수 (코드 중복 방지 및 FE 대응)
async def record_failure(task_id: str, error_msg: str):
    await db_instance.db.detection_tasks.update_one(
        {"task_id": task_id},
        {"$set": {
            "status": "failed",
            "result": {"error": error_msg}, # FE에서 읽을 수 있도록 구조화
            "updated_at": datetime.now()
        }}
    )
    print(f" [Task {task_id}] 분석 실패 기록됨: {error_msg}")
    

# 외부 엔진 실행을 위한 비동기 래퍼 함수
SYSTEM_SERVER_URL = "https://aloof-absurd-altitude.ngrok-free.dev"

async def run_system_engine(task_id: str, url: str, mode: str, user_id: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 복잡한 임베딩 데이터 대신 task_id만 전달
            await client.post(f"{SYSTEM_SERVER_URL}/analyze", json={
                "task_id": task_id
            })
    except Exception as e:
        await record_failure(task_id, f"엔진 호출 실패: {str(e)}")
             


# 탐지 요청 엔드포인트
@router.post("/analyze", response_model=DetectionResponse, summary="Detection Request")
async def analyze_content(
    request_in: DetectionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user) # 여기서 토큰 검사 및 유저 추출 
):
    # 1. URL 패턴에 따른 모드 결정 (추가됨)
    detected_mode = get_system_mode(str(request_in.url))
    
    # 2. 고유 Task ID 생성 및 유저 정보 추출
    task_id = str(uuid.uuid4())
    user_name = str(current_user.get("name", "Unknown")) 
    user_email = str(current_user.get("email", "No Email"))
    
    # 3. 저장할 데이터 준비 (target_name에 유저 이름을 자동 주입)
    new_task = {
        "task_id": task_id,
        "user_id": str(current_user["_id"]), 
        "user_email": user_email,
        "url": str(request_in.url),
        "target_name": user_name,  # 회원 이름 자동 주입
        "status": "processing",
        "mode": detected_mode,
        "result": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    try:
        await db_instance.db.detection_tasks.insert_one(new_task)    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB 기록 실패: {str(e)}"
        )

    # 4. 시스템 엔진 실행 명령어 준비
    # 주의: 프로젝트 루트의 system/main.py 경로 확인 필요
    script_path = os.path.join(os.getcwd(), "system", "main.py")
    
    command = [
        "python", # 윈도우 환경이라 python3 -> python으로 변경
        script_path, 
        str(request_in.url), 
        "--mode", detected_mode,
        "--task_id", task_id # 엔진이 결과를 업데이트할 수 있도록 task_id 전달
    ]

    # 5. 비동기로 시스템 실행 
    background_tasks.add_task(
        run_system_engine,
        task_id,
        str(request_in.url),
        detected_mode,
        str(current_user["_id"])
    )

    # 6. 즉시 응답 반환 (프론트엔드는 이 task_id로 폴링 시작)
    return {
        "task_id": task_id,
        "status": "processing",
        "mode": detected_mode,
        "result": None
    }


# 수집 데이터 저장 요청 엔드포인트
@router.post("/metadata", status_code=status.HTTP_201_CREATED, summary="Receive Metadata")
async def receive_engine_metadata(metadata_in: MetadataCreate):
    try:
        metadata_dict = metadata_in.model_dump()
        
        # 1. task_id가 실제로 존재하는지 확인
        task_exists = await db_instance.db.detection_tasks.find_one({"task_id": metadata_dict["task_id"]})
        if not task_exists:
            raise HTTPException(
                status_code=404, 
                detail=f"Task ID {metadata_dict['task_id']} not found. Metadata cannot be linked."
            )

        # 2. MongoDB 호환을 위한 URL 문자열 변환
        metadata_dict["target_url"] = str(metadata_dict["target_url"])
        
        # 3. 'metadata' 컬렉션에 저장
        result = await db_instance.db.metadata.insert_one(metadata_dict)
        
        return {
            "message": "Metadata saved successfully and linked to task",
            "task_id": metadata_dict["task_id"], # 연결된 ID를 응답에 포함
            "db_id": str(result.inserted_id)
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save metadata: {str(e)}"
        )
        
        
        
# 전체 탐지 목록 조회
@router.get("/history", response_model=List[DetectionDetailResponse], summary="Get Detection History")
async def get_detection_history(
    current_user: dict = Depends(get_current_user) # 1. [인증] 누구인지 확인
):

    # 2. 로그인한 유저의 고유 ID 추출
    user_id = str(current_user["_id"])
    
    # 3. [인가] 내 데이터만 조회하도록 필터링
    cursor = db_instance.db.detection_tasks.find({"user_id": user_id}).sort("created_at", -1)
    
    tasks = await cursor.to_list(length=100)
    
    return tasks



# 특정 작업 상세 조회 (새로고침용)
@router.get("/summary-report/{task_id}", response_model=DetectionDetailResponse, summary="Get Summary Result")
async def get_specific_result(task_id: str):

    task = await db_instance.db.detection_tasks.find_one({"task_id": task_id})
    
    if not task:
        raise HTTPException(status_code=404, detail="해당 작업을 찾을 수 없습니다.")
    
    return task


# 통합 조회 API
@router.get("/full-report/{task_id}", summary="Get Full Analysis Result")
async def get_full_report(
    task_id: str,
    current_user: dict = Depends(get_current_user) # 1. [인증] 누가 보려고 하는지 확인
):
    # 2. 'detection_tasks'에서 해당 task_id 찾기
    task = await db_instance.db.detection_tasks.find_one({"task_id": task_id})
    
    if not task:
        raise HTTPException(
            status_code=404, 
            detail=f"해당 Task_id를 찾을 수 없습니다."
        )

    # 3. [인가] 핵심 보안 체크
    if task.get("user_id") != str(current_user["_id"]):
        raise HTTPException(
            status_code=403, # 인증된 사용자이지만, 이 데이터에 접근 권한은 없을 경우
            detail="해당 리포트에 접근 권한이 없습니다."
        )

    # 4. 권한이 확인된 경우에만 상세 정보(metadata) 가져오기
    metadata = await db_instance.db.metadata.find_one({"task_id": task_id})
    
    # JSON 변환을 위해 _id 문자열 처리
    task["_id"] = str(task["_id"])
    if metadata:
        metadata["_id"] = str(metadata["_id"])
        
    return {
        "task_id": task_id,
        "analysis_result": task,
        "server_details": metadata
    }
    
    
@router.patch("/tasks/{task_id}")
async def update_task_result(
    task_id: str,
    body: TaskUpdateRequest,
):
    # 상태값 검증: 오직 completed 또는 failed만 허용
    allowed_statuses = ["completed", "failed"]
    if body.status not in allowed_statuses:
        # 엔진이 잘못된 상태를 보내면 400 에러로 거절
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않는 상태값입니다. ({', '.join(allowed_statuses)} 중 하나여야 함)"
        )
    
    
    # 1. 업데이트할 데이터 준비
    update_data = {
        "status": body.status, 
        "result": {
            "metadata": body.metadata.dict() if body.metadata else None,
            "results": [r.dict() for r in body.results] if body.results else [],
            "screenshot_path": body.screenshot_path,
            "report_path": body.report_path,
        },
        "updated_at": datetime.now()
    }

    # 2. MongoDB 업데이트 실행
    # task_id가 문자열이므로 필터링하여 $set 명령어로 수정
    result = await db_instance.db.detection_tasks.update_one(
        {"task_id": task_id}, 
        {"$set": update_data}
    )

    # 3. 해당 Task가 존재하는지 확인
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="해당 태스크를 찾을 수 없습니다.")

    return {
        "message": f"작업 상태가 {body.status}로 업데이트되었습니다.",
        "task_id": task_id,
    }
    
    
@router.get("/tasks/{task_id}/details", summary="Get Task Details for System Engine")
async def get_task_details_for_engine(task_id: str):
    # 1. 태스크 정보 조회
    task = await db_instance.db.detection_tasks.find_one({"task_id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. 해당 유저의 얼굴 프로필 조회
    profile = await db_instance.db.face_profiles.find_one({"user_id": task["user_id"]})
    
    return {
        "task_id": task_id,
        "url": task["url"],
        "mode": task["mode"],
        "target_embedding": profile["avg_embedding"] if profile else None,
        "user_id": task["user_id"]
    }