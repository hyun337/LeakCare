# 🔍 LeakCare
AI 기반 딥페이크 및 불법 유출물 통합 탐지·대응 플랫폼

### 🛠 Tech Stack
- AI: PyTorch, insightface (ArcFace buffalo_l), BiSeNet, ConvNeXt-Tiny
- Backend: FastAPI, MongoDB Atlas, JWT
- Frontend: React 19, Vite 7
- System: Playwright, httpx, ReportLab, Anthropic API (Claude)
- Tools: GitHub, Discord, Swagger

### 👥 Team Members
- 김수진: AI Specialist
     - 핵심 역할: 인물 식별 및 유사도 분석 엔진 고도화
     - 주요 업무
        - insightface (ArcFace buffalo_l) 기반 512차원 얼굴 임베딩 추출
        - 코사인 유사도 기반 얼굴 비교 알고리즘 구현
        - 불법 촬영(임계값 0.6) / 딥페이크(임계값 0.5) 이중 임계값 실험 및 설정
        - ConvNeXt-Tiny 기반 딥페이크 탐지 모델(v12) 학습 및 성능 검증
        - BiSeNet 기반 얼굴 파싱 모델을 활용한 눈·코·입 가림 여부 검증

- 남지민: Frontend Eng.
     - 핵심 역할: 피해 대응 프로세스 시각화 및 사용자 경험 최적화
     - 주요 업무
        - React 19 + Vite 기반의 인터랙티브 사용자 UI 구현
        - 피해 현황 및 분석 진행 상태 실시간 모니터링 대시보드 개발 (5초 폴링)
        - 증거 보고서 조회 및 삭제 요청 관리 인터페이스 구축
        - 얼굴 등록 페이지, 탐지 요청 페이지, 결과 보고서 페이지, 삭제 요청서 페이지 구현

- 박민서: Backend Eng.
     - 핵심 역할: 시스템 통합 및 데이터 흐름 제어
     - 주요 업무
        - FastAPI 기반 비동기 RESTful API 서버 설계 및 구축
        - MongoDB Atlas 스키마 설계 및 데이터 무결성 관리
        - JWT + bcrypt 기반 사용자 인증 및 보안 처리
        - Pydantic 스키마 기반 입력값 검증 및 파일 위변조 방지
        - 얼굴 임베딩 평균 벡터 산출 및 face_profiles 컬렉션 관리

- 이서현: System Eng.
     - 핵심 역할: 정밀 채증 및 원천 데이터 수집 파이프라인 구축
     - 주요 업무
        - Playwright 기반 헤드리스 브라우저 실시간 웹페이지 접속 및 스크린샷 자동화
        - 이미지 외 메타데이터(서버 IP, 국가/도시, 타임스탬프) 추출 로직 개발
        - 봇 탐지 우회(webdriver 제거, User-Agent 설정, 추적 도메인 차단) 전략 수립
        - asyncio.Semaphore(5) 기반 병렬 이미지 분석 처리 구현
        - ReportLab 기반 PDF 증거 보고서 자동 생성
        - Claude API (Haiku 4.5) 연동 다국어 삭제 요청문 자동 생성

### 시스템 구조 설계
```
leakcare/ (Root)
├── .gitignore               # GitHub 제외 파일 설정 (.env, 모델 가중치 등)
├── README.md                # 전체 프로젝트 실행 및 설치 가이드
├── requirements.txt         # 전체 라이브러리 목록 (pip install -r)
│
├── system/ (이서현)
│   ├── main.py              # 채증 엔진 최상위 진입점 및 CLI 인터페이스
│   ├── server.py            # FastAPI 기반 SYS 서버 (/analyze 엔드포인트)
│   ├── browser/             # 브라우저 구동 관련
│   │   ├── manager.py       # Playwright 브라우저 생성 및 세션 관리
│   │   └── stealth.py       # 봇 탐지 우회(Stealth) 설정
│   ├── core/                # 핵심 수집 기능
│   │   ├── capture.py       # 실시간 스크린샷 및 Lazy Loading 강제 로드
│   │   └── extractor.py     # 서버 IP, 국가/도시, 이미지 URL, 게시물 링크 추출
│   └── utils/               # 공통 도구
│       ├── file_path.py     # 증거 파일 경로 생성 및 관리
│       ├── report.py        # ReportLab 기반 PDF 증거 보고서 생성
│       └── llm.py           # Claude API 연동 다국어 삭제 요청문 생성
│
├── AI/ (김수진)
│   ├── analyze.py           # 얼굴 유사도 비교 및 딥페이크 탐지 통합 분석
│   ├── register.py          # 얼굴 등록 및 임베딩 추출
│   ├── config.py            # 모델 설정 및 임계값 관리
│   ├── models/
│   │   └── face_parsing.pth # BiSeNet 얼굴 파싱 모델 가중치
│   ├── detection/
│   │   ├── face_detector.py # 6단계 얼굴 등록 검증 파이프라인
│   │   └── face_parser.py   # BiSeNet 기반 눈·코·입 가림 여부 검증
│   └── deepfake/
│       └── deepfake_detector.py      # ConvNeXt-Tiny 기반 딥페이크 탐지
│       └── deepfake_detector_v12.pth # 파인튜닝된 딥페이크 탐지 모델 가중치
│
├── backend/ (박민서)
│   ├── app/
│   │   ├── main.py          # FastAPI 서버 진입점 및 미들웨어 설정
│   │   ├── api/v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── detection.py  # 탐지 요청 수신 및 SYS 엔진 호출
│   │   │   │   ├── faces.py      # 얼굴 사진 등록 및 임베딩 관리
│   │   │   │   ├── reports.py    # 보고서 조회 및 삭제 요청문 반환
│   │   │   │   └── users.py      # 회원가입, 로그인, 비밀번호 변경
│   │   │   └── dependencies.py   # JWT 토큰 기반 인증 의존성
│   │   ├── core/
│   │   │   ├── config.py    # 환경변수 로드 (pydantic-settings)
│   │   │   ├── database.py  # MongoDB Atlas 연결 및 세션 관리
│   │   │   └── security.py  # bcrypt 해시, JWT 토큰 생성/검증
│   │   ├── schemas/         # Pydantic 기반 요청/응답 데이터 스키마
│   │   │   ├── detection.py
│   │   │   ├── face.py
│   │   │   ├── report.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   └── selector.py  # URL 패턴 분석 기반 분석 모드 결정
│   │   └── utils/
│   │       └── file_validator.py  # 파일 MIME 타입 검증 (위변조 방지)
│   └── ai/                  # BE 내 얼굴 등록용 AI 모듈
│       ├── register.py
│       └── detection/
│           ├── face_detector.py
│           └── face_parser.py
│
└── frontend/ (남지민)
    ├── public/              # 정적 파일 (로고, 파비콘 등)
    ├── src/
    │   ├── api/             # 백엔드 통신 관련
    │   │   ├── client.js    # Base URL 및 공통 헤더 설정
    │   │   ├── detectApi.js # 탐지 요청 API
    │   │   ├── jobApi.js    # 작업 목록 조회 API
    │   │   ├── photoApi.js  # 얼굴 사진 등록/조회/삭제 API
    │   │   ├── reportApi.js # 보고서 조회 및 삭제 요청문 API
    │   │   └── userApi.js   # 회원가입, 로그인, 비밀번호 변경 API
    │   ├── components/
    │   │   └── layout/
    │   │       └── MainLayout.jsx  # 상단 네비게이션 및 공통 레이아웃
    │   ├── pages/
    │   │   ├── Login.jsx           # 로그인 페이지
    │   │   ├── Register.jsx        # 회원가입 페이지
    │   │   ├── Dashboard.jsx       # 메인 현황 대시보드
    │   │   ├── PhotoManagement.jsx # 얼굴 사진 등록 및 관리
    │   │   ├── DetectRequest.jsx   # 탐지 요청 페이지
    │   │   ├── JobList.jsx         # 작업 목록 및 실시간 폴링
    │   │   ├── ReportList.jsx      # 결과 보고서 목록
    │   │   ├── Result.jsx          # 보고서 상세 페이지
    │   │   └── DeleteRequest.jsx   # 삭제 요청서 확인 페이지
    │   ├── routes/
    │   │   └── AppRouter.jsx       # React Router 라우팅 설정
    │   ├── styles/                 # 페이지별 CSS 파일
    │   ├── App.jsx                 # 앱 루트 컴포넌트
    │   └── main.jsx                # 리액트 시작점
    ├── index.html
    ├── vite.config.js
    └── package.json
```
