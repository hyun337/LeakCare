import cv2
import numpy as np
import os
import asyncio
from insightface.app import FaceAnalysis

# 모델 초기화 (서버 실행 시 한 번만 로드되도록 설정)
app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

# 전역 변수로 타겟 임베딩 관리
CURRENT_TARGET_EMBEDDING = None

def load_target_embedding(image_path_or_bytes):
    """
    분석의 기준이 되는 '사용자 얼굴' 임베딩을 로드
    파일 경로(str)나 바이너리(bytes) 모두 처리 가능
    """
    global CURRENT_TARGET_EMBEDDING
    
    if isinstance(image_path_or_bytes, str):
        img = cv2.imread(image_path_or_bytes)
    else:
        nparr = np.frombuffer(image_path_or_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        print("❌ 타겟 이미지를 로드할 수 없습니다.")
        return False

    faces = app.get(img)
    if len(faces) == 0:
        print("❌ 타겟 이미지에서 얼굴을 찾을 수 없습니다.")
        return False

    # 가장 큰 얼굴의 임베딩 추출 및 정규화
    emb = faces[0].embedding
    CURRENT_TARGET_EMBEDDING = emb / np.linalg.norm(emb)
    print("🎯 분석 타겟 임베딩 로드 완료")
    return True

async def analyze_face_bytes(image_bytes: bytes):
    """
    수집된 이미지(바이너리)를 현재 로드된 타겟 임베딩과 비교
    """
    if CURRENT_TARGET_EMBEDDING is None:
        return {"match": False, "score": 0.0, "error": "No target loaded"}

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"match": False, "score": 0.0}

    faces = app.get(img)
    if len(faces) == 0:
        return {"match": False, "score": 0.0}

    best_score = 0.0
    for face in faces:
        if face.embedding is None: continue
        # 수집된 얼굴 임베딩 정규화
        emb = face.embedding / np.linalg.norm(face.embedding)
        # 코사인 유사도 계산
        score = float(np.dot(CURRENT_TARGET_EMBEDDING, emb))
        
        if score > best_score:
            best_score = score

    # 임계값 0.60 적용 (통합 테스트 결과에 따라 조절 가능)
    return {"match": best_score >= 0.60, "score": round(best_score, 4)}
