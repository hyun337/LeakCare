from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # ← 추가
from pydantic import BaseModel
from typing import List
import asyncio
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.main import run_analysis

app = FastAPI(title="LeakCare System Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ evidence 폴더를 /reports 경로로 정적 서빙
evidence_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence")
os.makedirs(evidence_dir, exist_ok=True)
app.mount("/reports", StaticFiles(directory=evidence_dir), name="reports")


class AnalyzeRequest(BaseModel):
    task_id: str


@app.get("/health")
async def health():
    return {"status": "ok", "message": "System 서버 정상 동작 중"}


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    asyncio.create_task(
        run_analysis_by_task_id(req.task_id)
    )
    print(f"🚀 분석 시작됨 | task_id: {req.task_id}")
    return {
        "message": "분석이 시작되었습니다.",
        "task_id": req.task_id
    }


async def run_analysis_by_task_id(task_id: str):
    from system.main import run_analysis_by_task_id as _run
    await _run(task_id)
