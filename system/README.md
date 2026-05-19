- ### 가상환경
  source .venv/bin/activate 

- ### 서버 (터미널 2개)
  - uvicorn system.server:app --host 0.0.0.0 --port 8001
  - ngrok http 8001 
