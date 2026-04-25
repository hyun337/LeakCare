import magic
from fastapi import UploadFile

async def validate_file_signature(file: UploadFile):
    # 1. 파일의 앞부분(시그니처 섹션) 읽기
    header = await file.read(2048)
    # 2. 읽은 후 포인터를 다시 처음으로
    await file.seek(0)
    # 3. 실제 파일 종류(MIME type) 분석
    mime = magic.from_buffer(header, mime=True)
    # 4. 허용할 형식 리스트
    allowed_types = [
        "image/jpeg", 
        "image/png", 
    ]
    
    return mime in allowed_types