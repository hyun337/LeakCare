from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.core.database import db_instance
from app.api.v1.dependencies import get_current_user
from app.schemas.report import RemovalTextResponse, ReportDetailResponse, ReportListItem

router = APIRouter()

# 1. 보고서 목록 조회
@router.get("/", response_model=List[ReportListItem])
async def get_reports_list(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    # 상태가 'completed'인 task들만 최신순으로 가져옴
    cursor = db_instance.db.detection_tasks.find(
        {"user_id": user_id, "status": "completed"},
        {"_id": 0, "task_id": 1, "url": 1, "created_at": 1, "mode": 1}
    ).sort("created_at", -1)
    
    return await cursor.to_list(length=100)

# 2. task별 상세 조회 & PDF 경로 반환
@router.get("/{task_id}", response_model=ReportDetailResponse)
async def get_report_detail(task_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    report = await db_instance.db.detection_tasks.find_one(
        {"task_id": task_id, "user_id": user_id}
    )
    
    if not report:
        raise HTTPException(status_code=404, detail="보고서를 찾을 수 없습니다.")
        
    return {
        "task_id": report["task_id"],
        "url": report["url"],
        "status": report["status"],
        "result": report.get("result"),
        "pdf_url": f"/api/v1/reports/download/{task_id}", # PDF 다운로드 경로
        "created_at": report["created_at"]
    }

# 3. 삭제 요청서 텍스트 조회 
@router.get("/{task_id}/removal-text", response_model=RemovalTextResponse)
async def get_removal_request_text(task_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    
    report = await db_instance.db.detection_tasks.find_one(
        {"task_id": task_id, "user_id": user_id}
    )
    
    # 1. report가 None인 경우(데이터를 못 찾은 경우) 먼저 체크
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="해당 분석 요청을 찾을 수 없습니다."
        )
        
    # 2. 상태가 아직 'completed'가 아닌 경우 (분석 중)
    if report.get("status") != "completed":
        return {"text": "현재 AI 분석이 진행 중입니다. 잠시만 기다려 주세요!"}
    
    # 3. 분석은 끝났으나 텍스트가 아직 비어있는 경우 (예외 케이스)
    result_data = report.get("result")
    removal_text = result_data.get("removal_request_text") if result_data else None
    
    if not removal_text:
        return {"text": "리포트가 준비되었으나 생성된 삭제 요청 문구가 없습니다. 시스템 관리자에게 문의해 주세요."}
        
    # 4. 정상적으로 텍스트가 있는 경우
    return {"text": removal_text}