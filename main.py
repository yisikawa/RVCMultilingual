import os
import argparse
from core import setup_logging
from core.config import AppConfig
from core.pipeline import AudioPipeline

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Multi-language RVC Base Audio Generator")
    parser.add_argument("--text", type=str, required=True, help="Input Japanese text")
    parser.add_argument("--lang", type=str, required=True, help="Target language (e.g., French, English, Spanish)")
    parser.add_argument("--code", type=str, required=True, help="Language code for TTS (e.g., fr-FR, en-US, es-ES)")
    parser.add_argument("--char", type=str, default="", help="Character setting/personality")
    parser.add_argument("--out", type=str, default="translated_base.mp3", help="Output audio file name")
    parser.add_argument("--rvc_model", type=str, default=None, help="RVC Model Name or Path (Optional)")
    parser.add_argument("--run_rvc", action="store_true", help="Set this flag to run RVC conversion after TTS")

    args = parser.parse_args()

    print(f"--- Translating: {args.text} to {args.lang} ---")
    try:
        config = AppConfig.load()
        config.rvc_source_path = args.out
        
        if args.rvc_model:
            config.rvc_model = args.rvc_model
            
        pipeline = AudioPipeline(config)
        
        translated_text, output_path = pipeline.translate_and_synthesize(
            args.text, args.lang, args.code, args.char
        )
        print(f"Translated: {translated_text}")
        print(f"Successfully generated base audio: {output_path}")
        
        if args.run_rvc and config.rvc_model:
            print("--- Running RVC Conversion ---")
            success = pipeline.run_rvc_conversion()
            if success:
                print(f"RVC Conversion successful! Saved to: {config.rvc_output_path}")
            else:
                print("RVC Conversion failed.")
        elif args.run_rvc:
            print("To run RVC conversion, please specify --rvc_model or save it in settings.")
        else:
            print("Next step: Use this audio with your RVC model for voice conversion.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()
