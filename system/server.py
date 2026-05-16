import asyncio
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.main import run_analysis_by_task_id
from system.utils.file_path import get_project_root

app = FastAPI(title="LeakCare System Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    task_id: str

@app.get("/health")
async def health():
    return {"status": "ok", "message": "System 서버 정상 동작 중"}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    if not req.task_id:
        raise HTTPException(status_code=400, detail="task_id가 비어있습니다.")
    asyncio.create_task(run_analysis_by_task_id(req.task_id))
    print(f"🚀 분석 시작됨 | task_id: {req.task_id}")
    return {"message": "분석이 시작되었습니다.", "task_id": req.task_id}

@app.get("/reports/{filename}")
async def download_report(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="잘못된 파일명입니다.")
    path = os.path.join(get_project_root(), "evidence", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    return FileResponse(path, media_type="application/pdf", filename=filename)
