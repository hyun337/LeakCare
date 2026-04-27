import cv2
import numpy as np
import os
import asyncio
from insightface.app import FaceAnalysis

# 1. 모델 초기화 (기존 유지)
app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

def get_target_embedding(image_path):
    """
    로컬 이미지 파일에서 얼굴 특징(Embedding)을 추출하고 정규화합니다.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ 이미지를 불러올 수 없습니다: {image_path}")
        return None
    
    faces = app.get(img)
    if len(faces) == 0:
        print(f"❌ 얼굴을 찾을 수 없습니다: {image_path}")
        return None
    
    # 가장 선명한(첫 번째) 얼굴의 임베딩 추출 및 L2 정규화
    emb = faces[0].embedding
    return emb / np.linalg.norm(emb)

# 2. 타겟 이미지 로드 설정
TARGET_FOLDER = "targets"
# 프로젝트 폴더에 'targets' 폴더가 없다면 생성
if not os.path.exists(TARGET_FOLDER):
    os.makedirs(TARGET_FOLDER)
    print(f"📁 '{TARGET_FOLDER}' 폴더를 생성했습니다. 테스트할 사진을 넣어주세요.")

# 폴더 내 이미지 파일 리스트 확보
target_files = [f for f in os.listdir(TARGET_FOLDER) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

# ─────────────────────────────
# [동적 타겟 로드] 하드코딩된 벡터 대신 파일을 읽어옴
# ─────────────────────────────
REGISTERED_EMBEDDING = None
if target_files:
    # 가장 먼저 발견된 이미지를 타겟으로 설정
    target_path = os.path.join(TARGET_FOLDER, target_files[0])
    REGISTERED_EMBEDDING = get_target_embedding(target_path)
    if REGISTERED_EMBEDDING is not None:
        print(f"🎯 타겟 로드 완료: {target_files[0]} (분석 준비 완료)")
else:
    print("⚠️ 'targets' 폴더가 비어있습니다. 분석 시 매칭 결과가 항상 False로 나옵니다.")

async def analyze_face_bytes(image_bytes: bytes):
    """
    엔진에서 넘어온 이미지 바이너리를 타겟 얼굴과 비교합니다.
    """
    if REGISTERED_EMBEDDING is None:
        return {"match": False, "score": 0.0, "error": "No target loaded"}

    # 바이너리를 이미지로 변환
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return {"match": False, "score": 0.0}

    # 현재 이미지에서 얼굴 탐지
    faces = app.get(img)
    if len(faces) == 0:
        return {"match": False, "score": 0.0}

    best_score = 0.0
    for face in faces:
        if face.embedding is None: continue
        emb = face.embedding / np.linalg.norm(face.embedding)
        score = float(np.dot(REGISTERED_EMBEDDING, emb))
        
        if score > best_score:
            best_score = score

    # 유사도 임계값: 0.60
    return {"match": best_score >= 0.60, "score": round(best_score, 4)}

# ─────────────────────────────
# 테스트용 메인 실행부
# ─────────────────────────────
if __name__ == "__main__":
    async def test():
        # 테스트할 이미지가 폴더에 있다면 실행
        test_img = "test_mult.png"
        if os.path.exists(test_img):
            with open(test_img, "rb") as f:
                image_bytes = f.read()
            result = await analyze_face_bytes(image_bytes)
            print(f"🔍 테스트 결과: {result}")
        else:
            print(f"ℹ️ 테스트용 이미지({test_img})가 없어 실행을 생략합니다.")

    asyncio.run(test())
