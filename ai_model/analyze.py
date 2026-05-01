import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_face_app, SIMILARITY_THRESHOLD_ILLEGAL, SIMILARITY_THRESHOLD_DEEPFAKE
from deepfake.deepfake_detector import DeepfakeDetector

class Analyze:
    def __init__(self):
        self.app = get_face_app()
        self.deepfake_detector = DeepfakeDetector(
            weights_path=os.path.join(os.path.dirname(__file__),
                                    "deepfake/deepfake_efficientnet_b4.pth")
        )

    def analyze(self, registered_embeddings, image):
        # 이미지 로드 실패 방어 로직
        if image is None:
            return {"error": "이미지를 불러올 수 없습니다.", "face_count": 0, "results": []}

        faces = self.app.get(image)

        if len(faces) == 0:
            return {"face_count": 0, "results": []}

        results = []
        for i, face in enumerate(faces):
            if face.embedding is None:
                continue
            
            # 수집이미지 정규화
            emb = face.embedding / np.linalg.norm(face.embedding)

            # 사용자 임베딩과 코사인 유사도 계산
            scores = [float(np.dot(reg_emb, emb)) for reg_emb in registered_embeddings]

            # 가장 높은 유사도를 최종 본인 일치 점수로 선택
            best_score = max(scores) if scores else 0.0

            # [deepfake_detector.py] 딥페이크 탐지용 얼굴 크롭
            bbox = face.bbox.astype(int)
            h, w = image.shape[:2]
            x1, y1 = max(0, bbox[0]), max(0, bbox[1])
            x2, y2 = min(w, bbox[2]), min(h, bbox[3])
            face_crop = image[y1:y2, x1:x2]

            if face_crop.size == 0:
                df_result = {"is_deepfake": False, "confidence": 0.0}
            else:
                df_result = self.deepfake_detector.detect(face_crop)
                
            # 딥페이크 여부에 따라 다른 임계값 적용
            threshold = SIMILARITY_THRESHOLD_DEEPFAKE if df_result["is_deepfake"] else SIMILARITY_THRESHOLD_ILLEGAL
            if best_score >= threshold:
                percent = 80 + (best_score - threshold) / (1.0 - threshold) * 20
            else:
                percent = (best_score / threshold) * 80
            percent = round(min(100, max(0, percent)), 1)
            status = "위험" if percent >= 80 else "의심" if percent >= 50 else "안전"

            results.append({
                "face_index": i,
                "best_score": round(best_score, 4),
                "all_scores": [round(s, 4) for s in scores],
                "is_deepfake": df_result["is_deepfake"],
                "percent": percent,
                "status": status
            })

        return {
            "face_count": len(results),
            "results": results
        }


if __name__ == "__main__":
    import cv2

    IMAGE_PATH = "../data/test_images/son.png"

    app = get_face_app()
    analyzer = Analyze()

    reg_image = cv2.imread(IMAGE_PATH)
    faces = app.get(reg_image)
    reg_emb = faces[0].embedding
    reg_emb = reg_emb / np.linalg.norm(reg_emb)

    scan_image = cv2.imread(IMAGE_PATH)
    result = analyzer.analyze([reg_emb], scan_image)

    print(f"얼굴 수: {result['face_count']}")
    for r in result["results"]:
        print(f"  얼굴 {r['face_index']} | 유사도: {r['best_score']} | 딥페이크: {r['is_deepfake']} | {r['percent']}% ({r['status']})")
