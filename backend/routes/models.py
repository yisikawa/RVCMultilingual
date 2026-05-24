import os
from fastapi import APIRouter

router = APIRouter()
MODELS_DIR = "models"

@router.get("/models")
async def list_models():
    if not os.path.isdir(MODELS_DIR):
        return {"pth": [], "index": []}
    files = os.listdir(MODELS_DIR)
    pth = sorted([f"models/{f}" for f in files if f.endswith(".pth")])
    index = sorted([f"models/{f}" for f in files if f.endswith(".index")])
    return {"pth": pth, "index": index}
