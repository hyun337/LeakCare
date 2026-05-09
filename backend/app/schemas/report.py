from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

# 보고서 목록용 간단한 정보
class ReportListItem(BaseModel):
    task_id: str
    url: str
    mode: str
    created_at: datetime

# 보고서 상세 정보
class ReportDetailResponse(BaseModel):
    task_id: str
    url: str
    status: str
    result: Optional[Any] = None
    pdf_url: str
    created_at: datetime

# 삭제 요청서 텍스트 응답
class RemovalTextResponse(BaseModel):
    text: str