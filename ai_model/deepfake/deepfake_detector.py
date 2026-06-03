
import cv2
import torch
from torchvision import transforms
import timm
import sys
import os

# config.py import
# AI/config.py 구조라면 아래 경로 유지
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import DEEPFAKE_THRESHOLD
except ImportError:
    # config.py가 없거나 import 실패할 경우 기본값 사용
    DEEPFAKE_THRESHOLD = 0.5


class DeepfakeDetector:
    def __init__(self, weights_path: str = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model()

        if weights_path and os.path.exists(weights_path):
            checkpoint = torch.load(weights_path, map_location=self.device)

            # 저장 방식이 여러 가지일 수 있어서 대응
            if isinstance(checkpoint, dict):
                if "model_state_dict" in checkpoint:
                    self.model.load_state_dict(checkpoint["model_state_dict"])
                elif "state_dict" in checkpoint:
                    self.model.load_state_dict(checkpoint["state_dict"])
                else:
                    self.model.load_state_dict(checkpoint)
            else:
                self.model.load_state_dict(checkpoint)

            print(f"파인튜닝 가중치 로드 완료: {weights_path}")
        else:
            print("파인튜닝 가중치 없음 또는 경로 오류")

        self.model.eval()

        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        print(f"DeepfakeDetector 초기화 완료 | device: {self.device}")
        print(f"Threshold: {DEEPFAKE_THRESHOLD}")

    def _build_model(self):
        model = timm.create_model(
            "convnext_tiny",
            pretrained=False,
            num_classes=2
        )
        model.to(self.device)
        return model

    def detect(self, face_image):
        """
        cv2 이미지(BGR)를 입력받아 딥페이크 여부 탐지
        face_image: cv2.imread()로 읽은 BGR 이미지
        """

        if face_image is None:
            raise ValueError("입력 이미지가 비어 있습니다.")

        # OpenCV는 BGR이므로 RGB로 변환
        face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

        input_tensor = self.transform(face_rgb).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)  # shape: [1, 2]
            probabilities = torch.softmax(output, dim=1).squeeze().cpu().numpy()

        # 네 학습 코드 기준:
        # real = 0
        # fake = 1
        real_prob = float(probabilities[0])
        fake_prob = float(probabilities[1])

        score = fake_prob
        is_deepfake = score >= DEEPFAKE_THRESHOLD
        confidence = score if is_deepfake else 1 - score

        return {
            "is_deepfake": bool(is_deepfake),
            "confidence": round(float(confidence), 4),
            "score": round(float(score), 4),
            "real_prob": round(real_prob, 4),
            "fake_prob": round(fake_prob, 4),
            "threshold": DEEPFAKE_THRESHOLD
        }

    def detect_image(self, image_path: str):
        """
        이미지 파일 경로 1개를 받아 딥페이크 여부 탐지
        """

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"이미지를 읽을 수 없습니다: {image_path}")

        return self.detect(image)


# ==============================
# VSCode에서 사진 1장 테스트용 코드
# ==============================
if __name__ == "__main__":
    # 1. 여기에 네 가중치 파일 경로 입력
    weights_path = r"deepfake/deepfake_detector_v12.pth"

    # 2. 여기에 테스트할 이미지 경로 입력
    image_path = r"son_fake.jpg"

    detector = DeepfakeDetector(weights_path=weights_path)

    result = detector.detect_image(image_path)

    print("\n===== 딥페이크 탐지 결과 =====")
    print(f"이미지 경로: {image_path}")

    if result["is_deepfake"]:
        print("판정: Fake / Deepfake 의심")
    else:
        print("판정: Real / 실제 이미지 가능성 높음")

    print(f"Confidence: {result['confidence']}")
    print(f"Score(Fake 확률 기준): {result['score']}")
    print(f"Real 확률: {result['real_prob']}")
    print(f"Fake 확률: {result['fake_prob']}")
    print(f"Threshold: {result['threshold']}")
