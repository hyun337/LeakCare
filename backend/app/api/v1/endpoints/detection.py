from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from typing import List, Optional
from app.schemas.metadata import MetadataCreate 
from app.schemas.detection import DetectionRequest, DetectionResponse, DetectionDetailResponse
from app.core.database import db_instance
import uuid
import asyncio
import random
from datetime import datetime
from app.api.v1.dependencies import get_current_user
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

router = APIRouter()

# 가상 AI 분석 로직
async def mock_ai_analysis(url: str):

    await asyncio.sleep(5)  # 5초간 분석하는 척 대기
    
    score = random.randint(15, 98)
    items = ["email", "password", "api_key", "db_credential"]
    
    return {
        "score": score,
        "leaked_items": random.sample(items, random.randint(1, 3)),
        "is_malicious": score > 70,
        "ai_description": f"해당 사이트 분석 결과 위험도 {score}점이 감지되었습니다."
    }


async def run_analysis_and_update(task_id: str, url: str):
    browser = None
    try:
        async with async_playwright() as p:
            # 리눅스 서버 환경에서 안정적인 구동을 위한 필수 옵션들 추가
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage" # 메모리 부족 에러 방지
                ]
            )
            context = await browser.new_context()
            page = await context.new_page()
            
            # 페이지 이동 (에러 상세 확인을 위해 에러 로그 출력 추가)
            try:
                await page.goto(url, timeout=25000, wait_until="domcontentloaded")
                page_title = await page.title()
                result_data = {"status": "completed", "title": page_title}
            except Exception as inner_e:
                result_data = {"status": "failed", "error": f"Page Load Error: {str(inner_e)}"}

    except Exception as e:
        # 전체 로직 에러 캐치 및 상세 내용 기록
        error_msg = f"Detail: {repr(e)}"
        result_data = {"status": "failed", "error": error_msg}
        print(f"!!! [TASK FAILED] {task_id}: {error_msg}") # Render 로그에서도 확인 가능


# 탐지 요청 엔드포인트
@router.post("/analyze", response_model=DetectionResponse, summary="Detection Request")
async def analyze_content(
    request_in: DetectionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user) # 여기서 토큰 검사 및 유저 추출 
):
    
    # 가짜 작업 ID 생성 
    task_id = str(uuid.uuid4())
    
    # 1. DB 저장
    new_task = {
        "task_id": task_id,
        "user_id": str(current_user["_id"]), # 로그인한 유저의 실제 DB 고유 ID
        "user_email": current_user["email"], # 관리용 이메일
        "url": str(request_in.url),
        "target_name": request_in.target_name,
        "status": "processing",
        "result": None,
        "created_at": datetime.now()
    }
    await db_instance.db.detection_tasks.insert_one(new_task)

    # 2. 비동기로 분석 작업 시작 (사용자가 기다리지 않도록)
    background_tasks.add_task(run_analysis_and_update, task_id, str(request_in.url))    
    
    return {
        "task_id": task_id,
        "status": "processing",
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