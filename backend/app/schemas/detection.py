from pydantic import BaseModel, HttpUrl, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

# 탐지 요청
class DetectionRequest(BaseModel):
    # HttpUrl: http/https가 포함된 실제 URL 형식인지 검증
    # Field: URL 최대 길이를 2083자(브라우저 표준)로 제한하여 DoS 공격 방어    
    url: HttpUrl = Field(
        ..., 
        description="분석할 사이트의 URL",
        max_length=2083   
    )
    
    # target_name: 한글/영문/숫자만 허용하여 스크립트 주입(XSS) 차단
    target_name: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        pattern=r"^[a-zA-Z0-9가-힣ㄱ-ㅎㅏ-ㅣ\s\-_]+$",
        description="분석 대상자 이름 (특수문자 불가)"
    )

# 탐지 결과 응답 - 분석 현황
class DetectionResponse(BaseModel):
    task_id: str = Field(..., description="작업 고유 ID")
    status: str = Field(..., pattern="^(processing|completed|failed)$") # 상태값 고정
    result: Optional[Dict[str, Any]] = None
    
# 상세 결과 조회 응답 - DB 조회
class DetectionDetailResponse(BaseModel):
    task_id: str
    url: str  
    target_name: Optional[str] = None
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime

    # 몽고디비 데이터를 Pydantic으로 변환할 때 필요한 설정
    model_config = ConfigDict(from_attributes=True)