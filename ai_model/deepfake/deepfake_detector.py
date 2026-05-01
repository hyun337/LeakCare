"""
모듈 5: 딥페이크 탐지
EfficientNet-B4 기반으로 얼굴 이미지가 딥페이크(AI 합성)인지 판별합니다.
파인튜닝 데이터셋: Kaggle 140k Real and Fake Faces (fake=0, real=1)
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DEEPFAKE_THRESHOLD


class DeepfakeDetector:
    def __init__(self, weights_path: str = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._build_model()

        # 파인튜닝 가중치 로드
        if weights_path and os.path.exists(weights_path):
            self.model.load_state_dict(
                torch.load(weights_path, map_location=self.device)
            )
            print(f"파인튜닝 가중치 로드 완료: {weights_path}")
        else:
            print("파인튜닝 가중치 없음")

        self.model.eval()

        # 데이터 전처리리
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((380, 380)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
        print(f"DeepfakeDetector 초기화 완료 (device: {self.device})")

    # 모델 아키텍처
    def _build_model(self):
        model = efficientnet_b4(weights=EfficientNet_B4_Weights.IMAGENET1K_V1)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.4),
            nn.Linear(in_features, 1)
        )
        model.to(self.device)
        return model

    def detect(self, face_image):
        # BGR → RGB
        face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

        # 전처리 + 추론
        input_tensor = self.transform(face_rgb).unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            # 레이블 방향 반전 (fake=0, real=1 score 높을수록 딥페이크)
            score = 1 - torch.sigmoid(output).item()

        is_deepfake = score >= DEEPFAKE_THRESHOLD
        confidence = score if is_deepfake else 1 - score

        return {
            "is_deepfake": is_deepfake,
            "confidence": round(confidence, 4)
        }
        
# ============ 직접 실행 시 테스트 ============
if __name__ == "__main__":
    import sys

    detector = DeepfakeDetector(
        weights_path=os.path.join(os.path.dirname(__file__), 
                                  "deepfake_efficientnet_b4.pth")
    )

    # 테스트 이미지 경로 (실제 이미지로 변경하세요)
    test_images = [
        ("real", "data/test_images/son2.png"),
        ("fake", "data/test_images/deepfake4.png"),
    ]

    for label, path in test_images:
        if not os.path.exists(path):
            print(f"[{label}] 이미지 없음: {path}")
            continue

        image = cv2.imread(path)
        result = detector.detect(image)

        print(f"[{label}]  is_deepfake: {result['is_deepfake']}\n" 
              f"confidence: {result['confidence']}")
