### 라이브러리 설치
``` pip install torch torchvisionpip insightface opencv-python onnxruntime numpy scikit-learn Pillow gdown ```

### 모델 폴더 생성
``` mkdir models ```

### 모델 다운로드
``` gdown https://drive.google.com/uc?id=154JgKpzCPW82qINcVieuPH3fZ2e0P812 -O "models/face_parsing.pth" ```

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
└── verdict/
    └── judge.py                       # 종합 판정 (percent + status 반환)
