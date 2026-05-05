"""
System을 독립 FastAPI 서버로 띄움
BE가 subprocess 대신 HTTP POST로 분석 요청

실행 방법:
    uvicorn system.server:app --host 0.0.0.0 --port 8001

BE에서 호출 방법:
    POST http://System노트북IP:8001/analyze
    {
        "task_id": "...",
        "url": "https://...",
        "mode": "single",
        "embedding": [0.123, 0.456, ...]  // 512차원 float 리스트
    }
"""

import asyncio
import os
import sys
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# 프로젝트 루트를 파이썬 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.main import run_analysis

app = FastAPI(title="LeakCare System Engine")

# BE에서 요청할 수 있도록 CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────
# 요청 스키마
# ─────────────────────────────
class AnalyzeRequest(BaseModel):
    task_id: str
    url: str
    mode: str = "single"
    embedding: List[float]  # BE의 face_profiles.avg_embedding (512차원)


# ─────────────────────────────
# 엔드포인트
# ─────────────────────────────
@app.get("/health")
async def health():
    """서버 상태 확인용"""
    return {"status": "ok", "message": "System 서버 정상 동작 중"}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """
    BE에서 분석 요청을 받아 백그라운드로 실행합니다.
    바로 200 응답을 반환하고, 분석은 백그라운드에서 진행됩니다.
    완료 후 BE의 PATCH /detection/tasks/{task_id} 로 결과를 전송합니다.
    """
    if not req.embedding:
        raise HTTPException(status_code=400, detail="임베딩이 비어있습니다.")

    if len(req.embedding) != 512:
        raise HTTPException(
            status_code=400,
            detail=f"임베딩 차원이 올바르지 않습니다. 기대: 512, 실제: {len(req.embedding)}"
        )

    # numpy 배열로 변환
    registered_embeddings = [np.array(req.embedding)]

    # 백그라운드로 분석 실행 (응답은 바로 반환)
    asyncio.create_task(
        run_analysis(
            task_id=req.task_id,
            url=req.url,
            mode=req.mode,
            registered_embeddings=registered_embeddings
        )
    )

    print(f"🚀 분석 시작됨 | task_id: {req.task_id} | url: {req.url} | mode: {req.mode}")

    return {
        "message": "분석이 시작되었습니다.",
        "task_id": req.task_id
    }
