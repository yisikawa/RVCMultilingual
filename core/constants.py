# 対応言語マップ（表示名 → BCP-47コード）
LANGUAGE_MAP: dict[str, str] = {
    "Japanese": "ja-JP",
    "English": "en-US",
    "French": "fr-FR",
    "Spanish": "es-ES",
    "Chinese": "zh-CN",
    "Korean": "ko-KR",
    "German": "de-DE",
    "Italian": "it-IT",
}

# サポートする言語の一覧
SUPPORTED_LANGUAGES: list[str] = list(LANGUAGE_MAP.keys())

# Geminiモデル名
GEMINI_MODEL_NAME: str = "gemini-2.0-flash"

# RVCデフォルト設定
DEFAULT_PITCH: int = 0
DEFAULT_F0_METHOD: str = "rmvpe"
DEFAULT_INDEX_RATE: float = 0.75
DEFAULT_TARGET_SR: int = 44100

# デフォルト音声パス
DEFAULT_RVC_INPUT: str = "rvc_input.wav"
DEFAULT_RVC_OUTPUT: str = "rvc_result.wav"
