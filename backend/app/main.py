from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.v1.api import api_router

app = FastAPI(title="LeakCare")

# CORS 설정 추가
origins = [
    "http://localhost:5173",    # 프론트엔드 개발 서버 주소
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # 허용할 도메인 목록
    allow_credentials=True,           # 쿠키 허용 여부
    allow_methods=["*"],              # 모든 HTTP 메서드(GET, POST 등) 허용
    allow_headers=["*"],              # 모든 HTTP 헤더 허용
)

# 서버 시작 시 실행
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

# 서버 종료 시 실행
@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Server is running"}

app.include_router(api_router, prefix="/api/v1")


# 에러별 메시지 설정
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # 발생한 모든 에러 목록 가져오기
    errors = exc.errors()
    
    # 첫 번째 에러가 발생한 필드 이름 확인
    # 보통 loc은 ['body', 'password'] 형식이므로 마지막 요소를 가져옴 
    error_field = errors[0]['loc'][-1]
    
    # 필드별 맞춤 메시지 설정
    if error_field == "password":
        msg = "비밀번호는 8자 이상 15자 이하로 설정해 주세요."
    elif error_field == "target_name":
        msg = "이름은 한글, 영문, 숫자와 일부 특수문자(-, _)만 사용 가능합니다."
    elif error_field == "url":
        msg = "올바른 URL 주소를 입력해 주세요.(http/https 포함)"
    else:
        msg = "입력하신 정보가 형식에 맞지 않습니다. 다시 확인해 주세요."

    return JSONResponse(
        status_code=422,
        content={
            "detail": msg,
            "error_field": error_field  # 어떤 필드가 틀렸는지 
        }
    )