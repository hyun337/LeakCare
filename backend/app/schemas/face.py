from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from typing import Optional

class FacePhotoInfo(BaseModel):
    photo_index: int = Field(..., description="사진의 순서")
    registered_at: datetime = Field(..., description="등록 일시")
    url: Optional[str] = Field(None, description="사진이 저장된 URL 경로")

class FaceRegisterResponse(BaseModel):
    success: bool = Field(..., description="등록 성공 여부")
    message: str = Field(..., description="결과 메시지")
    photo_index: int = Field(..., description="방금 등록된 사진의 번호 (1~5)")
    photo_count: int = Field(..., description="현재까지 등록된 총 사진 수")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "얼굴 등록 완료 (1/5)",
                "photo_index": 1,
                "photo_count": 1
            }
        }

class FaceStatusResponse(BaseModel):
    user_id: str = Field(..., description="사용자 고유 ID")
    photo_count: int = Field(..., description="현재 등록된 사진 수")
    max_photos: int = Field(..., description="최대 등록 가능 사진 수")
    photos: List[FacePhotoInfo] = Field(default=[], description="등록된 사진 상세 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "60d5ecb8b39d1c001f8e4e5a",
                "photo_count": 3,
                "max_photos": 5,
                "photos": [
                    {"photo_index": 1, "created_at": "2026-05-06T17:00:00"},
                    {"photo_index": 2, "created_at": "2026-05-06T17:05:00"},
                    {"photo_index": 3, "created_at": "2026-05-06T17:10:00"}
                ]
            }
        }
        
class FaceDeleteResponse(BaseModel):
    success: bool
    message: str
    photo_count: int