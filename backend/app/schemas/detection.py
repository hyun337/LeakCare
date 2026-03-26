from pydantic import BaseModel, HttpUrl
from typing import Optional

# 탐지 요청할 때 (URL, 이름)
class DetectionRequest(BaseModel):
    url: HttpUrl # 유효한 URL 형식인지 자동 검증
    target_name: str # 분석 대상자 이름

# 탐지 결과 응답 (임시 가짜 데이터)
class DetectionResponse(BaseModel):
    task_id: str # 분석 작업 고유 ID
    status: str # processing, completed, failed
    result: Optional[dict] = None # 실제 AI 분석 결과가 들어갈 자리