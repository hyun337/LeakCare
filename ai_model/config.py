
# 얼굴 감지
FACE_DETECTION_THRESHOLD = 0.5      # 얼굴 감지 최소 신뢰도 (0~1)
MIN_FACE_SIZE = 50                   # 얼굴 최소 크기 (픽셀)
MAX_REGISTER_IMAGES = 5              # 등록 최대 이미지 수

# 유사도 비교
SIMILARITY_THRESHOLD_ILLEGAL = 0.6   # 불법촬영 유출물 임계값
SIMILARITY_THRESHOLD_DEEPFAKE = 0.5  # 딥페이크 유출물 임계값

# 딥페이크 탐지 
DEEPFAKE_THRESHOLD = 0.5             # 딥페이크 판정 임계값

# 모델 경로
ARCFACE_MODEL_NAME = "buffalo_l"     # insightface 모델 이름

# 이미지 품질
MIN_BLUR_SCORE = 100.0               # 라플라시안 분산 최소값 (낮을수록 흐림)
MIN_BRIGHTNESS = 40                   # 최소 평균 밝기 (0~255)
MAX_BRIGHTNESS = 220                  # 최대 평균 밝기 (0~255)

# 얼굴 각도 허용 범위 (도)
MAX_YAW = 30                          # 좌우 회전 최대 허용 각도
MAX_PITCH = 25                        # 상하 회전 최대 허용 각도
MAX_ROLL = 20                         # 기울기 최대 허용 각도

# 공유 모델 인스턴스 
from insightface.app import FaceAnalysis

_shared_app = None

def get_face_app():
    global _shared_app
    if _shared_app is None:
        _shared_app = FaceAnalysis(
            name=ARCFACE_MODEL_NAME,
            providers=['CPUExecutionProvider']
        )
        _shared_app.prepare(ctx_id=0, det_size=(640, 640))
    return _shared_app
