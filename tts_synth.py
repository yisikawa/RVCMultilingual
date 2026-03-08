import os
from google.cloud import texttospeech
from dotenv import load_dotenv

load_dotenv()

def synthesize_multilingual_text(text, language_code, voice_name=None, output_file="output.mp3"):
    """
    Google Cloud Text-to-Speechを使用してテキストを音声に変換します。
    """
    # GOOGLE_APPLICATION_CREDENTIALS は環境変数として設定されている必要があります
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)

    # 言語コードと音声の設定
    # 例: 'en-US', 'fr-FR', 'zh-CN'
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        pitch=0,
        speaking_rate=1.0
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{output_file}"')

if __name__ == "__main__":
    # テスト用
    try:
        sample_text = "Bonjour, comment allez-vous ?"
        synthesize_multilingual_text(sample_text, "fr-FR", "fr-FR-Neural2-A")
    except Exception as e:
        print(f"Error: {e}")
