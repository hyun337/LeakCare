from passlib.context import CryptContext

# 암호화 알고리즘 설정 (bcrypt 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # 비밀번호를 암호화(해시)
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 입력받은 비밀번호와 DB의 암호화된 비밀번호가 일치하는지 확인
    return pwd_context.verify(plain_password, hashed_password)