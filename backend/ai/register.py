import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from detection.face_detector import FaceDetector

class Register:
    def __init__(self):
        self.detector = FaceDetector()

    def register(self, image_input):

        # 검증 + 임베딩 추출
        result = self.detector.validate_for_registration(image_input)

        if not result["success"]:
            return {
                "success": False,
                "step": result["step"],
                "embedding": None
            }

        # L2 정규화
        embedding = result["embedding"]
        embedding = embedding / np.linalg.norm(embedding)

        return {
            "success": True,
            "step": "pass",
            "embedding": embedding.tolist()
        }


# 테스트 
if __name__ == "__main__":
    import json

    register = Register()

    test_image = "../data/test_images/jgtest_mask.jpg"

    result = register.register(test_image)

    output = {
        "success": result["success"],
        "step": result["step"],
        "embedding": result["embedding"][:5] if result["embedding"] else None
    }
    print(json.dumps(output, indent=4, ensure_ascii=False))
