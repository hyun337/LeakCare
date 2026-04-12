from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from datetime import datetime
import numpy as np
import cv2
import asyncio

from app.core.database import db_instance
from app.api.v1.dependencies import get_current_user
from app.schemas.face import FaceRegisterResponse, FaceStatusResponse

MAX_PHOTOS = 5

router = APIRouter()


@router.post("/register", response_model=FaceRegisterResponse, summary="Register Face Photo")
async def register_face(
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])

    # 1. 현재 등록된 사진 수 확인
    photo_count = await db_instance.db.face_photos.count_documents({"user_id": user_id})
    if photo_count >= MAX_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"최대 {MAX_PHOTOS}장까지 등록 가능합니다."
        )

    # 2. 업로드된 이미지를 numpy 배열로 변환
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미지를 읽을 수 없습니다. jpg/png 파일을 사용해주세요."
        )

    # 3. AI 검증 및 임베딩 추출 (동기 함수 → 비동기로 실행)
    register = request.app.state.register
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, register.register, image)

    # 4. 검증 실패 시 단계별 메시지 반환
    if not result["success"]:
        step_messages = {
            "load":  "이미지를 불러올 수 없습니다.",
            "1":     "얼굴이 감지되지 않았습니다.",
            "2":     "얼굴이 2명 이상 감지되었습니다. 1명만 있는 사진을 사용해주세요.",
            "3":     "얼굴이 너무 작습니다. 더 가까이 찍은 사진을 사용해주세요.",
            "4-1":   "정면 사진을 사용해주세요. (좌우/상하 각도 초과)",
            "4-2":   "눈, 코, 입이 가려지지 않은 사진을 사용해주세요.",
            "5":     "얼굴 인식 신뢰도가 낮습니다. 더 선명한 사진을 사용해주세요.",
        }
        msg = step_messages.get(result["step"], "얼굴 검증에 실패했습니다.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    # 5. 개별 임베딩 DB 저장
    photo_index = photo_count + 1
    await db_instance.db.face_photos.insert_one({
        "user_id": user_id,
        "photo_index": photo_index,
        "embedding": result["embedding"],  # 512차원 list
        "registered_at": datetime.now()
    })

    # 6. 평균 임베딩 업데이트
    await _update_avg_embedding(user_id)

    new_count = photo_count + 1
    return {
        "success": True,
        "message": f"얼굴 등록 완료 ({new_count}/{MAX_PHOTOS})",
        "photo_index": photo_index,
        "photo_count": new_count
    }


@router.get("/status", response_model=FaceStatusResponse, summary="Get Face Registration Status")
async def get_face_status(
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    photo_count = await db_instance.db.face_photos.count_documents({"user_id": user_id})

    return {
        "user_id": user_id,
        "photo_count": photo_count,
        "max_photos": MAX_PHOTOS
    }


async def _update_avg_embedding(user_id: str):
    """등록된 모든 임베딩의 평균을 계산해 face_profiles에 저장합니다."""
    cursor = db_instance.db.face_photos.find(
        {"user_id": user_id},
        {"embedding": 1, "_id": 0}
    )
    photos = await cursor.to_list(length=MAX_PHOTOS)

    embeddings = np.array([p["embedding"] for p in photos])
    avg_embedding = np.mean(embeddings, axis=0).tolist()

    await db_instance.db.face_profiles.update_one(
        {"user_id": user_id},
        {"$set": {
            "avg_embedding": avg_embedding,
            "photo_count": len(photos),
            "updated_at": datetime.now()
        }},
        upsert=True  # 없으면 새로 생성, 있으면 업데이트
    )
