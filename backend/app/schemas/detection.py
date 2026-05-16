from pydantic import BaseModel, HttpUrl, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

# 사용자의 탐지 요청 (FE -> BE)
class DetectionRequest(BaseModel):
    # HttpUrl: http/https가 포함된 실제 URL 형식인지 검증
    # Field: URL 최대 길이를 2083자(브라우저 표준)로 제한하여 DoS 공격 방어    
    url: HttpUrl = Field(
        ..., 
        description="분석할 사이트의 URL",
        max_length=2083   
    )
    
    
# 탐지 요청 직후 응답 (BE -> RE)
class DetectionResponse(BaseModel):
    task_id: str = Field(..., description="작업 고유 ID")
    status: str = Field(..., pattern="^(processing|completed|failed)$") # 상태값 고정
    mode: str = Field(..., description="판정된 분석 모드 (single/board)")
    result: Optional[Dict[str, Any]] = None
    
# 상세 결과 조회 응답 (BE -> FE)
class DetectionDetailResponse(BaseModel):
    task_id: str
    url: str  
    target_name: Optional[str] = None
    status: str = Field(..., pattern="^(processing|completed|failed)$")
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # 몽고디비 데이터를 Pydantic으로 변환할 때 필요한 설정
    model_config = ConfigDict(from_attributes=True)
    
    
# Sys 전용 결과 업데이트 스키마 (Sys -> BE)    
class DetectionMetadata(BaseModel):
    ip_address: str = Field(..., description="탐지된 서버 IP", example="211.234.56.78")
    country: str = Field(..., description="국가 정보", example="South Korea")
    city: str = Field(..., description="도시 정보", example="Asan")
    collected_at: str = Field(..., description="수집 일시", example="2026-05-08T13:44:00")

class DetectionResult(BaseModel):
    url: str = Field(..., description="탐지된 이미지/영상 URL")
    page_url: str = Field(..., description="데이터가 발견된 페이지 주소")
    score: float = Field(..., description="AI 분석 신뢰도 점수 (0~1)")
    matched: Optional[bool] = None
    is_deepfake: Optional[bool] = None
    risk_level: Optional[str] = None
    thumbnail_local_path: Optional[str] = None
    reason: Optional[str] = None

class TaskUpdateRequest(BaseModel):
    # 상태 머신 고정: 오직 아래 3가지 상태만 허용
    status: str = Field(
        ..., 
        pattern="^(processing|completed|failed)$",
        description="완료 시 completed, 실패 시 failed"
    )
    metadata: DetectionMetadata = Field(..., description="서버 위치 및 수집 정보")
    results: List[DetectionResult] = Field(default=[], description="상세 탐지 리스트")
    screenshot_path: Optional[str] = Field(None, description="분석 스크린샷 저장 경로")
    report_path: Optional[str] = Field(None, description="생성된 최종 PDF 리포트 파일 경로")
    removal_request_text: Optional[str] = Field(None, description="LLM 생성 삭제 요청 메일 텍스트") 

       
    
    
