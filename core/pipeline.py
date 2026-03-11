import logging
from core.config import AppConfig
from core.translator import GeminiTranslator
from core.tts_engine import TTSEngine
from core.rvc_engine import RVCEngine

logger = logging.getLogger(__name__)

class AudioPipeline:
    """翻訳→TTS→RVC変換のパイプライン（オーケストレーター）"""
    
    def __init__(self, config: AppConfig):
        self._config = config
        self._translator = None
        self._tts = None
        self._rvc = None
    
    def _get_translator(self):
        if self._translator is None:
            self._translator = GeminiTranslator(self._config.gemini_api_key)
        return self._translator
        
    def _get_tts(self):
        if self._tts is None:
            self._tts = TTSEngine(self._config.gcp_json_path)
        return self._tts
        
    def _get_rvc(self):
        if self._rvc is None:
            self._rvc = RVCEngine()
        return self._rvc

    def translate_and_synthesize(
        self, text: str, target_lang: str, lang_code: str, character_setting: str = ""
    ) -> tuple[str, str]:
        """翻訳とTTS合成を実行し、(翻訳テキスト, 出力ファイルパス)を返す"""
        translated = self._get_translator().translate(text, target_lang, character_setting)
        output_path = self._config.rvc_source_path
        self._get_tts().synthesize(translated, lang_code, output_file=output_path)
        return translated, output_path
    
    def run_rvc_conversion(self) -> bool:
        """RVC変換を実行する"""
        model_path = self._resolve_model_path(self._config.rvc_model)
        return self._get_rvc().convert(
            model_path=model_path,
            input_path=self._config.rvc_source_path,
            output_path=self._config.rvc_output_path,
        )
    
    def _resolve_model_path(self, model_path: str) -> str:
        """モデルパスを解決する"""
        import os
        if os.path.exists(model_path) or os.path.isabs(model_path):
            return model_path
        return os.path.join("RVC-models", model_path)
