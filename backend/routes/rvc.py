import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from core.config import AppConfig
from core.pipeline import AudioPipeline
from backend.job_manager import create_job, update_job

router = APIRouter()
_executor = ThreadPoolExecutor(max_workers=1)

class RVCRequest(BaseModel):
    rvc_model: str
    index_file: str = ""

def _run(job_id: str, req: RVCRequest, config: AppConfig) -> None:
    try:
        update_job(job_id, status="running", progress=10, message="モデル読み込み中...")
        config.rvc_model = req.rvc_model
        config.index_file = req.index_file
        pipeline = AudioPipeline(config)
        update_job(job_id, progress=30, message="RVC変換中...")
        success = pipeline.run_rvc_conversion()
        if success:
            update_job(job_id, status="done", progress=100, message="変換完了",
                       result={"audio_file": config.rvc_output_path})
        else:
            update_job(job_id, status="error", error="RVC変換に失敗しました")
    except Exception as e:
        update_job(job_id, status="error", error=str(e))

@router.post("/rvc")
async def run_rvc(req: RVCRequest):
    config = AppConfig.load()
    job_id = create_job()
    asyncio.create_task(run_in_threadpool(_run, job_id, req, config))
    return {"job_id": job_id}