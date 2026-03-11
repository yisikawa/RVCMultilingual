import os
import logging
from google.cloud import texttospeech

logger = logging.getLogger(__name__)

class TTSEngine:
    """Google Cloud TTSエンジン"""
    
    def __init__(self, gcp_json_path: str):
        if not gcp_json_path or not os.path.exists(gcp_json_path):
            raise ValueError(f"GCPの認証情報ファイルが見つかりませんまたは設定されていません: {gcp_json_path}")
        
        # 環境変数に設定（Google APIライブラリが読み取るため）
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_json_path
        self._client = texttospeech.TextToSpeechClient()
        
    def synthesize(self, text: str, language_code: str, voice_name: str | None = None, output_file: str = "output.mp3") -> bool:
        """テキストを音声に合成する"""
        logger.info(f"TTS合成を実行中... (Language: {language_code}, Output: {output_file})")
        
        input_text = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=0,
            speaking_rate=1.0
        )
        
        try:
            response = self._client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )
            
            with open(output_file, "wb") as out:
                out.write(response.audio_content)
                logger.info(f"音声ファイルを保存しました: {output_file}")
            return True
        except Exception as e:
            logger.error(f"TTS合成エラー: {e}")
            raise
