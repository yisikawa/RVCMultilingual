import os
import argparse
from gen_script import generate_multilingual_script
from tts_synth import synthesize_multilingual_text

def main():
    parser = argparse.ArgumentParser(description="Multi-language RVC Base Audio Generator")
    parser.add_argument("--text", type=str, required=True, help="Input Japanese text")
    parser.add_argument("--lang", type=str, required=True, help="Target language (e.g., French, English, Spanish)")
    parser.add_argument("--code", type=str, required=True, help="Language code for TTS (e.g., fr-FR, en-US, es-ES)")
    parser.add_argument("--voice", type=str, default=None, help="Specific voice name for TTS")
    parser.add_argument("--char", type=str, default="", help="Character setting/personality")
    parser.add_argument("--out", type=str, default="translated_base.mp3", help="Output audio file name")

    args = parser.parse_args()

    print(f"--- Translating: {args.text} to {args.lang} ---")
    try:
        translated_text = generate_multilingual_script(args.text, args.lang, args.char)
        print(f"Translated: {translated_text}")

        print(f"--- Synthesizing: {translated_text} ({args.code}) ---")
        synthesize_multilingual_text(translated_text, args.code, args.voice, args.out)
        
        print(f"Successfully generated base audio: {args.out}")
        print("Next step: Use this audio with your RVC model for voice conversion.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
