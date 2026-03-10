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
│   ├── __init__.py          # 패키지 인식용
│   ├── browser/             # 브라우저 구동 관련
│   │   ├── manager.py       # Playwright 브라우저 생성 및 세션 관리
│   │   └── stealth.py       # SNS 봇 탐지 우회(Stealth) 설정
│   ├── core/                # 핵심 수집 기능
│   │   ├── capture.py       # 실시간 스크린샷 및 PDF 증거 박제 로직 
│   │   └── extractor.py     # IP, 서버 위치, 타임스탬프 등 메타데이터 추출
│   └── utils/               # 공통 도구
│       └── file_path.py     # 캡처 파일 임시 저장 및 경로 관리
│
├── ai_model/ (김수진)      
│   ├── models/              # 학습된 가중치 파일(.pth) 저장 폴더
│   │   ├── face_detection.pth    # 얼굴 검출 모델 가중치
│   │   ├── feature_extract.pth   # 특징점 추출 모델 가중치
│   │   └── config.json           # 모델 버전 및 임계값(Threshold) 설정
│   ├── preprocessor.py      # 이미지 리사이징 및 68개 특징점 전처리
│   ├── analyzer.py          # 특징점 추출 및 유사도 계산
│   └── loader.py            # PyTorch 모델 로드 및 GPU/CPU 할당 설정 
│
├── backend/ (박민서)    
│   ├── api/                 # API 엔드포인트별 분리
│   │   ├── analysis.py      # 유출 분석 요청 수신 및 시스템 모듈 호출
│   │   ├── user.py          # 사용자 사진 등록 및 벡터 저장 관리
│   │   └── report.py        # PDF 보고서 생성 및 LLM 삭제 요청 메일 생성
│   ├── db/                  # MongoDB 연동 로직
│   │   ├── mongodb.py       # MongoDB Atlas 연결 및 세션 관리
│   │   └── schemas.py       # Pydantic을 이용한 데이터 규격 정의
│   ├── core/                # 공통 핵심 로직
│   │   ├── security.py      # SHA-256 해시 생성 및 무결성 검증
│   │   └── config.py        # .env 환경 변수 로드
│   └── main.py              # FastAPI 서버 진입점 및 라우터 통합
│
└── frontend/ (남지민)  
    ├── public/                  # 정적 파일 (로고, 파비콘 등)
    ├── src/
    │   ├── api/             # 백엔드 통신 관련
    │   │   ├── axios.js         # Axios 기본 설정 (Base URL, Timeout 등)
    │   │   └── analysis.js      # 분석 요청 및 결과 조회 API 함수들
    │   ├── components/      # UI 조각 (입력창, 결과 카드)
    │   │   ├── common/          # 공통 UI 
    │   │   │   ├── Header.jsx          # 로고와 메뉴가 있는 상단 바
    │   │   │   ├── Footer.jsx          # 하단 정보 바
    │   │   │   ├── Button.jsx          # 스타일 입혀진 공통 버튼
    │   │   │   ├── LoadingSpinner.jsx  # 분석 중일 때 보여줄 로딩 애니메이션
    │   │   ├── dashboard/       # 대시보드 전용
    │   │   │   ├── DetectionStatus.jsx # 분석 진행 현황 보여주는 요약 카드
    │   │   │   ├── ResultTable.jsx     # 탐지된 유출물 리스트 보여주는 표
    │   │   │   ├── EvidencePreview.jsx # 캡처된 이미지 미리 보여주는 창
    │   │   └── forms/          # 입력 양식
    │   │   │   ├── PhotoUpload.jsx     # 사진 등록하는 업로드 칸
    │   │   │   ├── UrlSubmit.jsx       # 의심 URL 입력하고 분석 버튼 누르는 칸
    │   ├── hooks/               # 커스텀 훅 (선택 사항 - 데이터 로딩 등)
    │   ├── pages/           # 전체 화면 (대시보드, 등록 페이지)
    │   │   ├── HomePage.jsx     # 서비스 소개 및 메인
    │   │   ├── RegisterPage.jsx # 내 사진(벡터) 등록 페이지
    │   │   ├── DashBoard.jsx    # 유출 분석 현황 대시보드
    │   │   └── ResultPage.jsx   # 상세 증거 보고서 확인 페이지
    │   └── styles/          # Tailwind CSS 디자인 설정
    │   │   └── index.css        # Tailwind CSS 설정 및 글로벌 스타일
    │   ├── utils/           # 공통 함수 (날짜 포맷 변경 등
    │   │   ├── Formatter.js     #서버에서 받은 날짜나 숫자를 읽기 변환하는 함수
    │   │   └── Validators.js    # 입력된 URL 형식이 맞는지, 이미지 용량이 너무 크지 않은지 체크하는 함수
    │   ├── App.jsx              # 전체 라우팅 설정 (React Router)
    │   └── main.jsx             # 리액트 시작점
    ├── .env                     # 백엔드 주소 등 환경 변수
    ├── index.html               # 메인 HTML 템플릿
    └── tailwind.config.js       # Tailwind CSS 상세 설정
    └── package.json         # 패키지 관리
