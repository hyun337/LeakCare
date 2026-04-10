from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MetadataCreate(BaseModel):
    task_id: str = Field(..., description="연결된 분석 작업 고유 ID")
    target_url: str = Field(..., description="수집 대상 URL")
    ip_address: str = Field(..., description="서버 IP 주소")
    country: Optional[str] = Field(None, description="서버 국가")
    city: Optional[str] = Field(None, description="서버 도시")
    screenshot_path: str = Field(..., description="저장된 증거 스크린샷 파일명 또는 경로")
    video_path: Optional[str] = None
    collector_id: str = Field("system_engine_01", description="수집기 식별자")
    collected_at: datetime = Field(default_factory=datetime.now)

class MetadataResponse(MetadataCreate):
    id: str = Field(..., description="데이터베이스 생성 ID (MongoDB _id)")