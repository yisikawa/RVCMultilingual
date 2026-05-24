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

class TranslateTTSRequest(BaseModel):
    text: str
    target_lang: str
    lang_code: str
    character_setting: str = ""

def _run(job_id: str, req: TranslateTTSRequest, config: AppConfig) -> None:
    try:
        update_job(job_id, status="running", progress=20, message="翻訳中...")
        pipeline = AudioPipeline(config)
        translated_text, audio_path = pipeline.translate_and_synthesize(
            req.text, req.target_lang, req.lang_code, req.character_setting
        )
        update_job(job_id, status="done", progress=100, message="完了",
                   result={"translated_text": translated_text, "audio_file": audio_path})
    except Exception as e:
        update_job(job_id, status="error", error=str(e))

@router.post("/translate-tts")
async def translate_tts(req: TranslateTTSRequest):
    config = AppConfig.load()
    job_id = create_job()
    asyncio.create_task(run_in_threadpool(_run, job_id, req, config))
    return {"job_id": job_id}