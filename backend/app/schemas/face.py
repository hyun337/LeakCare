from pydantic import BaseModel, Field
from typing import Optional

class FaceRegisterResponse(BaseModel):
    success: bool = Field(..., description="등록 성공 여부")
    message: str = Field(..., description="결과 메시지")
    photo_index: int = Field(..., description="현재 등록된 사진의 순서 (1~5)")
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

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "60d5ecb8b39d1c001f8e4e5a",
                "photo_count": 3,
                "max_photos": 5
            }
        }