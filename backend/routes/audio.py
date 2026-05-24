import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from core.config import AppConfig

router = APIRouter()

ALLOWED_FILES = {"rvc_input.wav", "rvc_result.wav"}

@router.get("/audio/{filename}")
async def get_audio(filename: str):
    if filename not in ALLOWED_FILES:
        raise HTTPException(status_code=403, detail="Access denied")
    path = os.path.join(os.getcwd(), filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="audio/wav")