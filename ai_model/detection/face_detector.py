import cv2
import numpy as np
from insightface.app import FaceAnalysis
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    FACE_DETECTION_THRESHOLD,
    MIN_FACE_SIZE,
    get_face_app,
    MAX_YAW,
    MAX_PITCH,
    MAX_ROLL,
)
from detection.face_parser import FaceParser

class FaceDetector:
    def __init__(self):
        self.app = get_face_app()
        self.face_parser = FaceParser()

    def validate_for_registration(self, image_input)
        # 이미지 로드
        image = self._load_image(image_input)
        if image is None:
            return self._fail("load")

        # 1단계 얼굴 감지
        faces = self.app.get(image)

        if len(faces) == 0:
            return self._fail("1")

        # 2단계 얼굴 수 확인
        if len(faces) > 1:
            return self._fail("2")

        face = faces[0]

        bbox = face.bbox.astype(int).tolist()
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        # 3단계 얼굴 크기
        if width < MIN_FACE_SIZE or height < MIN_FACE_SIZE:
            return self._fail("3")

        # 4단계 얼굴 각도
        pose_result = self._check_face_pose(face)
        if not pose_result["pass"]:
            return self._fail("4")

        # 5단계 얼굴 가림 검사 (Face Parsing)
        x1, y1, x2, y2 = bbox
        h, w = image.shape[:2]
        face_crop = image[max(0,y1):min(h,y2), max(0,x1):min(w,x2)]
        occlusion_result = self.face_parser.check_occlusion(face_crop)
        if not occlusion_result["pass"]:
            return self._fail("5")

        # 6단계 신뢰도
        confidence = float(face.det_score)

        if confidence < FACE_DETECTION_THRESHOLD:
            return self._fail("6")

        return {
            "success": True,
            "step": "pass",
            "embedding": face.embedding,
        }

    # 얼굴 각도 함수 (4단계)
    def _check_face_pose(self, face):
        yaw, pitch, roll = face.pose

        yaw = abs(float(yaw))
        pitch = abs(float(pitch))
        roll = abs(float(roll))

        if yaw > MAX_YAW or pitch > MAX_PITCH or roll > MAX_ROLL:
            return {"pass": False}

        return {"pass": True}

    # 실패
    def _fail(self, step):
        """실패 결과를 생성합니다."""
        return {
            "success": False,
            "step": step,
        }
    # 이미지 로드 함수
    def _load_image(self, image_input):
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
            if image is None:
                print(f"이미지를 불러올 수 없습니다: {image_input}")
            return image
        elif isinstance(image_input, np.ndarray):
            return image_input
        else:
            print(f"지원하지 않는 이미지 형식입니다: {type(image_input)}")
            return None


# 테스트
if __name__ == "__main__":
    detector = FaceDetector()

    test_image = "../../data/test_images/test_ok1.jpg"

    if os.path.exists(test_image):
        result = detector.validate_for_registration(test_image)

        print(f"success: {result['success']}")
        print(f"step: {result['step']}")
