import logging
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google")
import google.generativeai as genai
from core.constants import GEMINI_MODEL_NAME

logger = logging.getLogger(__name__)

class GeminiTranslator:
    """Gemini APIによる多言語翻訳クラス"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini APIキーが設定されていません")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    def translate(self, text: str, target_lang: str, character_setting: str = "") -> str:
        """テキストをターゲット言語に翻訳する"""
        prompt = self._build_prompt(text, target_lang, character_setting)
        response = self._model.generate_content(prompt)
        return response.text.strip()
    
    @staticmethod
    def _build_prompt(text: str, target_lang: str, character_setting: str) -> str:
        """翻訳プロンプトを構築する"""
        dialect_instruction = ""
        if "Hakata-ben" in target_lang:
            dialect_instruction = "\n4. 博多弁特有の語尾（〜と、〜ばい、〜ちゃん、〜けん等）や語彙を使い、地元の人のような自然な口調にしてください。"

        return f"""以下のテキストを{target_lang}に翻訳してください。

テキスト: {text}
設定: {character_setting}

要件:
1. 自然な話し言葉であること。
2. 音声合成（TTS）に適した形式であること。
3. 設定がある場合は、そのキャラクターらしい口調にすること。{dialect_instruction}

出力は翻訳後のテキストのみにしてください。"""
