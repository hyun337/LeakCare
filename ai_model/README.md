### 라이브러리 설치
``` pip install torch torchvisionpip insightface opencv-python onnxruntime numpy scikit-learn Pillow gdown ```

```
ai/
├── config.py                          # 설정값 + get_face_app() 공유 인스턴스
├── register.py                        # 등록: 검증 + 임베딩 추출 통합
├── analyze.py                         # 분석: 유사도 + 딥페이크 탐지 + 판정
├── detection/ 
│   ├── face_detector.py               # 5단계 얼굴 검증 + embedding 반환
│   └── face_parser.py                 # Face Parsing (가림 탐지)
├── deepfake/
│   ├── deepfake_detector.py           # 딥페이크 탐지
│   └── deepfake_efficientnet_b4.pth   # 파인튜닝한 모델
├── models/
│   └── face_parding.pth               # 가림탐지(face parsing) 모델
└──


```
[딥페이크 탐지 가중치 파일](https://drive.google.com/file/d/1myM2Z2nM7nACYW8W2FExeJR2B5e2HaN7/view?usp=sharing)


[Face Parsing 가중치 파일](https://drive.google.com/file/d/17aOAnvYOw0mFvihM7krab-VkN3rMHAKQ/view?usp=sharing)
