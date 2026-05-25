from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import translate_tts, rvc, audio, status, models

app = FastAPI(title="RVC Multilingual API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+):300\d$",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate_tts.router, prefix="/api")
app.include_router(rvc.router, prefix="/api")
app.include_router(audio.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(models.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}
