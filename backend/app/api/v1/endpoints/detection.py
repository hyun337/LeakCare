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


# [외부 엔진 실행을 위한 비동기 래퍼 함수]
async def run_system_engine(task_id: str, url: str, mode: str):
    """
    BackgroundTasks에 의해 실행될 실제 엔진 호출 함수
    """
    try:
        current_file = os.path.abspath(__file__)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file)))))
        
        path = current_file
        for _ in range(5):
            path = os.path.dirname(path)
        backend_root = path 
        
        script_path = os.path.join(backend_root, "system", "main.py")
        
        print(f"--- 경로 디버깅 ---")
        print(f"계산된 엔진 경로: {script_path}")
        print(f"파일 존재 여부: {os.path.exists(script_path)}")
        print(f"------------------")
        
        if not os.path.exists(script_path):
             print(f"에러: {script_path} 경로에 파일이 없습니다. 폴더 구조를 확인하세요.")
             return
        
        # 윈도우 환경에서 가상환경 파이썬을 정확히 사용하도록 sys.executable 권장
        process = subprocess.Popen([
            sys.executable, script_path, 
            url, 
            "--mode", mode, 
            "--task_id", task_id
        ])
        
        print(f"시스템 엔진 실행 시작 (PID: {process.pid})")

    except Exception as e:
        print(f"엔진 실행 중 오류 발생: {str(e)}")


# 탐지 요청 엔드포인트
@router.post("/analyze", response_model=DetectionResponse, summary="Detection Request")
async def analyze_content(
    request_in: DetectionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user) # 여기서 토큰 검사 및 유저 추출 
):
    # 1. URL 패턴에 따른 모드 결정 (추가됨)
    detected_mode = get_system_mode(str(request_in.url))
    task_id = str(uuid.uuid4())
    
    # 현재 로그인한 유저의 정보를 추출
    user_name = str(current_user.get("name", "Unknown")) 
    user_email = str(current_user.get("email", "No Email"))
    
    # 2. 저장할 데이터 준비 (target_name에 유저 이름을 자동 주입)
    new_task = {
        "task_id": task_id,
        "user_id": str(current_user["_id"]), 
        "user_email": user_email,
        "url": str(request_in.url),
        "target_name": user_name,  # [자동화] 입력받지 않고 유저 이름으로 설정
        "status": "processing",
        "result": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }

    try:
        # DB 저장 시도
        insert_result = await db_instance.db.detection_tasks.insert_one(new_task)
        if not insert_result.acknowledged:
            raise Exception("DB acknowledge failed")
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB 기록 실패: {str(e)}"
        )

    # 3. 백그라운드에서 실제 '외부 엔진' 실행 (변경됨)
    background_tasks.add_task(run_system_engine, task_id, str(request_in.url), detected_mode)
    
    return {
        "task_id": task_id,
        "status": "processing",
        "mode": detected_mode, # 프론트 확인용
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
    # 1. 업데이트할 데이터 준비 (Pydantic 모델을 딕셔너리로 변환)
    update_data = {
        "status": body.status,
        "metadata": body.metadata.dict(), # 객체는 dict로 변환해서 저장
        "results": [r.dict() for r in body.results],
        "screenshot_path": body.screenshot_path,
        "updated_at": datetime.now() # 업데이트 시간 기록
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
        "message": "업데이트 성공", 
        "task_id": task_id,
        "modified_count": result.modified_count
    }