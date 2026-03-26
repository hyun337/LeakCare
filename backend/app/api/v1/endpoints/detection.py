from fastapi import APIRouter
from app.schemas.detection import DetectionRequest, DetectionResponse
import uuid # 가짜 task_id 생성용

router = APIRouter()

# GET에서 POST로 변경
@router.post("/analyze", response_model=DetectionResponse, summary="Detection Request")
async def analyze_content(request_in: DetectionRequest):

    print(f" 탐지 요청 - URL: {request_in.url}, 대상: {request_in.target_name}")

    # 가짜 분석 작업 ID 생성
    mock_task_id = str(uuid.uuid4())
    
    return {
        "task_id": mock_task_id,
        "status": "processing", # 즉시 결과를 주기 어렵기 때문에 '처리 중' 상태를 보냄
        "result": None
    }