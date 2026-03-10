# 🔍 LeakCare
AI 기반 딥페이크 및 불법 유출물 통합 탐지·대응 플랫폼

### 🛠 Tech Stack
- AI: PyTorch, Dlib, Kaggle Dataset
- Backend: FastAPI, MongoDB, Playwright
- Frontend: React, Tailwind CSS
- Tools: GitHub, Discord, Swagger

### 👥 Team Members
- 김수진: AI Specialist
     - 핵심 역할: 인물 식별 및 유사도 분석 엔진 고도화
     - 주요 업무
        - PyTorch 기반 69개 이상 얼굴 특징점 추출
        - 128/512 차원 벡터 임베딩 변환 및 비교 알고리즘 구현
        - Kaggle 데이터셋(DFDC, VGGFace2) 활용 모델 학습 및 성능 검증
        - 유사도 판별을 위한 최적의 임계값 실험 및 설정

- 남지민: Frontend Eng.
     - 핵심 역할: 피해 대응 프로세스 시각화 및 사용자 경험 최적화
     - 주요 업무
        - React 기반의 인터랙티브 사용자 UI 구현
        - 피해 현황 및 분석 진행 상태 실시간 모니터링 대시보드 개발
        - 증거 보고서 조회 및 삭제 요청 관리 인터페이스 구축
        - Tailwind CSS를 활용한 직관적이고 깔끔한 디자인 시스템 적용

- 박민서: Backend Eng.
     - 핵심 역할: 시스템 통합 및 데이터 흐름 제어
     - 주요 업무
        - FastApI 기반 비동기 API 서버 설계 및 구축
        - MongoDB Atlas 스키마 설계 및 데이터 무결성 관리
        - LLM(GPT?) 연동 다국어 삭제 요청 메일 생성 로직 구현
        - SHA-256 해시 기반 PDF 증거 보고서 생성 엔진 개발

- 이서현: System Eng.(Scarping)
     - 핵심 역할: 정밀 채증 및 원천 데이터 수집 파이프라인 구축
     - 주요 업무
        - Playwright 기반 실시간 웹페이지 접속 및 캡처 자동화
        - 이미지 외 메타데이터(IP, URL, 타임스탬프) 추출 로직 개발
        - 봇 탐지 우회(Stealth) 및 다중 플랫폼 대응 전략 수립
        - 수집된 데이터의 백엔드 전달 및 아카이빙 구조 설계
       
- ### 시스템 구조 설계
 leakcare/ (Root)
├── .gitignore               # GitHub 제외 파일 설정 (Kaggle 데이터, .env 등)
├── README.md                # 전체 프로젝트 실행 및 설치 가이드
├── requirements.txt         # 전체 라이브러리 목록 (pip install -r)
│
├── system/ (이서현)  
│   ├── browser/             # 브라우저 구동 관련
│   │   ├── manager.py       # Playwright 브라우저 생성 및 세션 관리
│   │   └── stealth.py       # SNS 봇 탐지 우회(Stealth) 설정
│   ├── core/                # 핵심 수집 기능
│   │   ├── capture.py       # 스크린샷 캡처 및 PDF 박제 로직 
│   │   └── extractor.py     # IP, 서버 위치, 타임스탬프 추출
│   └── utils/               # 공통 도구
│       └── file_path.py     # 캡처 파일 임시 저장 경로 관리
│
├── ai_model/ (김수진)      
│   ├── models/              # 학습된 가중치 파일 저장용 폴더
│   ├── preprocessor.py      # 이미지 리사이징 및 68개 특징점 전처리
│   ├── analyzer.py          # 특징점 추출 및 유사도 계산
│   └── loader.py            # PyTorch 모델 로드 및 GPU 설정 
│
├── backend/ (박민서)    
│   ├── api/                 # API 엔드포인트별 분리
│   │   ├── analysis.py      # 유출 분석 요청 및 상태 관리 
│   │   ├── user.py          # 사용자 얼굴 등록 관리 
│   │   └── report.py        # PDF 보고서 생성 및 메일 발송
│   ├── db/                  # MongoDB 연동 로직 
│   ├── core/                # SHA-256 해시, 보안 설정, .env 로드
│   └── main.py              # FastAPI 서버 진입점 
│
└── frontend/ (남지민)  
    ├── src/
    │   ├── api/             # 백엔드 호출 함수 모음
    │   ├── components/      # UI 조각 (입력창, 결과 카드)
    │   ├── pages/           # 전체 화면 (대시보드, 등록 페이지) 
    │   └── styles/          # Tailwind CSS 디자인 설정
    └── package.json         # 리액트 패키지 관리
