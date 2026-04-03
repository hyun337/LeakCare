- ### ‼️ 시작
  1. 환경 설정
    pip install playwright insightface onnxruntime-gpu opencv-python reportlab httpx playwright install chromium
  2. 실행 방법
    ❗️ source .venv/bin/activate → 터미널에 먼저 입력 (가상 환경)
    python main.py "https://example.com/post/1" --mode single
  3. 게시판 전체 분석
    python main.py "https://example.com/board" --mode board --start 1 --end 5


- ### ‼️ 주요 기능
  1. 웹 자동 탐색 및 채증
    - Playwright 기반 브라우저 자동화
    - 전체 페이지 스크린샷 캡처
    - Lazy loading 대응 (자동 스크롤)
  2. 이미지 수집
    - 단일 페이지/게시판 페이지 지원
    - 게시글 링크 자동 추출 (페이지네이션 포함)
    - 중복 제거 및 광고/불필요 이미지 필터링
  3. AI 얼굴 분석
    - InsightFace 기반 얼굴 인식
    - 사전 등록된 사용자 벡터ㅘ 유사도 비교
    - 유사도 0.85 이상 → 유출 의심 탐지
  4. 백엔드 연동
    - 분석 요청 API 호출
    - 메타데이터(IP, 위치, 이미지 URL 등) 전송
    - 실시간 데이터 동기화
  5. PDF 보고서 생성
    - 채증 정보 + 분석 결과 포함
    - 한글 폰트 지원
    - 증거 자료 자동 정리


- ### ‼️ 파일 구조
  LeakCare/
  ├── main.py                # 시스템 실행 메인 엔진
  ├── ai_module.py           # InsightFace 기반 AI 분석 모듈
  ├── system/
  │   ├── browser/
  │   │   ├── manager.py     # 브라우저 수명 주기 관리
  │   │   └── stealth.py     # 봇 탐지 우회 스크립트
  │   ├── core/
  │   │   ├── capture.py     # 스크린샷 및 스크롤 제어
  │   │   └── extractor.py   # 메타데이터 및 이미지 추출 로직
  │   └── utils/
  │       ├── file_path.py   # 파일 경로 및 진행 상태 관리
  │       └── report.py      # PDF 보고서 생성 엔진
  └── README.md


- ### ‼️ 동작 흐름
  [URL 입력]
      ↓
  [웹 페이지 접속]
      ↓
  [스크린샷 + IP/위치 수집]
      ↓
  [이미지 수집]
      ↓
  [AI 얼굴 분석]
      ↓
  [유출 의심 탐지]
      ↓
  [백엔드 전송]
      ↓
  [PDF 보고서 생성]
