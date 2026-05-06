from fastapi import  Depends, APIRouter, HTTPException, status
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserLogin
from app.core.database import db_instance
from app.core.security import get_password_hash
from app.core.security import verify_password
from app.core.security import create_access_token
from app.core.security import pwd_context # 비밀번호 해싱 도구
from bson import ObjectId # 몽고디비 ID 변환용
from fastapi.security import OAuth2PasswordRequestForm
from app.api.v1.dependencies import get_current_user
from app.schemas.user import PasswordChangeRequest

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user_in: UserCreate):
    # 1. 중복 이메일 체크 (이미 가입된 유저인지 확인)
    existing_user = await db_instance.db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")

    # 2. 비밀번호 암호화 (해시화)
    hashed_password = get_password_hash(user_in.password)

    # 3. 저장할 데이터 준비 (Pydantic 모델을 딕셔너리로 변환)
    user_data = {
        "name": user_in.name,
        "email": user_in.email,
        "hashed_password": hashed_password, # 생 비밀번호 대신 암호화된 값 저장
    }

    # 4. MongoDB에 저장
    result = await db_instance.db.users.insert_one(user_data)
    
    # 5. 저장된 데이터에 생성된 ID를 입혀서 반환
    user_data["_id"] = str(result.inserted_id)
    return user_data



@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):

    # 1. 문자열로 받은 ID를 몽고디비 전용 객체로 변환 (잘못된 형식이면 에러 발생)
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="유효하지 않은 ID 형식입니다.")

    # 2. DB에서 검색
    user = await db_instance.db.users.find_one({"_id": ObjectId(user_id)})

    # 3. 데이터가 없으면 404 에러
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    # 4. _id(ObjectId 객체)를 문자열로 변환
    user["_id"] = str(user["_id"])

    # 5. 조회된 데이터 반환 (Pydantic이 자동으로 id로 매핑)
    return user



@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_in: UserUpdate):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="유효하지 않은 ID 형식입니다.")

    # 1. 수정할 데이터 정리 (None이 아닌 값만 골라냄)
    update_data = {k: v for k, v in user_in.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 내용이 없습니다.")

    # 2. MongoDB 업데이트 명령 실행 ($set 연산자 사용)
    result = await db_instance.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

    # 3. 수정된 결과 확인
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # 4. 수정된 최신 데이터 다시 조회해서 반환
    updated_user = await db_instance.db.users.find_one({"_id": ObjectId(user_id)})
    updated_user["_id"] = str(updated_user["_id"])
    
    return updated_user



@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def withdraw_membership(
    current_user: dict = Depends(get_current_user)
):
    # 1. 현재 로그인한 사용자의 ID 추출
    user_id_obj = current_user["_id"]  # ObjectId 형태
    user_id_str = str(user_id_obj)     # 문자열 형태 (다른 컬렉션 조회용)

    try:
        # 2. 본인과 연관된 모든 데이터 연쇄 삭제 (Cascading Delete)
        # 각 컬렉션에 user_id가 저장되어 있는 모든 문서 삭제
        
        # 탐지 기록 삭제
        await db_instance.db.detection_tasks.delete_many({"user_id": user_id_str})
        
        # 얼굴 프로필 및 사진 데이터 삭제
        await db_instance.db.face_profiles.delete_many({"user_id": user_id_str})
        await db_instance.db.face_photos.delete_many({"user_id": user_id_str})
        
        # 메타데이터 삭제
        await db_instance.db.metadata.delete_many({"user_id": user_id_str})

        # 3. 'users' 컬렉션에서 본인 계정 삭제
        result = await db_instance.db.users.delete_one({"_id": user_id_obj})

        # 4. 삭제 확인 (이미 로그인된 유저라 실패할 확률은 적지만 검증)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")

        # 204 No Content 반환
        return None

    except Exception as e:
        print(f"[Withdrawal Error] 본인 탈퇴 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="회원 탈퇴 처리 중 서버 오류가 발생했습니다.")



@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    
    # 1. 이메일(username)로 유저 찾기
    user = await db_instance.db.users.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")

    # 2. 비밀번호 검증 (user_in.password -> form_data.password로 수정)
    if not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")

    # 3. JWT 토큰 생성
    access_token = create_access_token(data={"sub": user["email"]})
    
    # 4. 로그인 성공 응답
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": str(user["_id"]), 
        "name": user["name"]
    }
    
    
@router.post("/change-pw", summary="change password")
async def change_password(
    body: PasswordChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    # 1. 현재 비밀번호가 맞는지 확인
    # current_user["hashed_password"]는 DB에 저장된 암호화된 비밀번호
    if not pwd_context.verify(body.current_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다."
        )

    # 2. 새 비밀번호와 이전 비밀번호가 같은지 체크
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호는 기존 비밀번호와 다르게 설정해 주세요."
        )

    # 3. 새 비밀번호 해싱
    new_hashed_password = pwd_context.hash(body.new_password)

    # 4. DB 업데이트
    await db_instance.db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"hashed_password": new_hashed_password}}
    )

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

