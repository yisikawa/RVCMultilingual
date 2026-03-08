import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def generate_multilingual_script(text, target_lang, character_setting=""):
    """
    Geminiを使用してテキストを指定の言語に翻訳し、自然な台本を生成します。
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in .env file")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""
    以下のテキストを{target_lang}に翻訳してください。
    
    テキスト: {text}
    設定: {character_setting}
    
    要件:
    1. 自然な話し言葉であること。
    2. 音声合成（TTS）に適した形式であること。
    3. 設定がある場合は、そのキャラクターらしい口調にすること。
    
    出力は翻訳後のテキストのみにしてください。
    """
    
    response = model.generate_content(prompt)
    return response.text.strip()

if __name__ == "__main__":
    # テスト用
    try:
        sample_text = "こんにちは、今日はとてもいい天気ですね。"
        result = generate_multilingual_script(sample_text, "French", "元気な女の子")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
