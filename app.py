import streamlit as st
import os
import json
from gen_script import generate_multilingual_script
from tts_synth import synthesize_multilingual_text
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)

# 設定の初期読み込みと手動変更の反映
current_config = load_config()
if "config" not in st.session_state or st.session_state.get("_last_config_str") != json.dumps(current_config):
    st.session_state["config"] = current_config
    st.session_state["_last_config_str"] = json.dumps(current_config)

st.set_page_config(page_title="Multi-language RVC Base Generator", layout="wide")

st.title("🌐 Multi-language RVC Base Generator")
st.markdown("Geminiで翻訳し、Google TTSで高品質なベース音声を生成します。")

# サイドバー：設定
with st.sidebar:
    st.header("⚙️ API & Model Settings")
    
    # セッション状態またはファイルから初期値を取得
    def_gemini_key = st.session_state["config"].get("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
    def_gcp_path = st.session_state["config"].get("gcp_json_path", os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""))
    def_rvc_model = st.session_state["config"].get("rvc_model", "")
    def_index_file = st.session_state["config"].get("index_file", "")
    def_rvc_source = st.session_state["config"].get("rvc_source_path", "rvc_input.wav")
    def_rvc_output = st.session_state["config"].get("rvc_output_path", "rvc_result.wav")

    gemini_key = st.text_input("Gemini API Key", value=def_gemini_key, type="password")
    gcp_json_path = st.text_input("GCP Service Account JSON Path", value=def_gcp_path)
    
    st.divider()
    st.header("🎙️ RVC Settings")
    rvc_model_path = st.text_input("RVC Model Name / Path", value=def_rvc_model, placeholder="e.g. haruka_v2.pth")
    index_file = st.text_input("Index File Path", value=def_index_file, placeholder="e.g. added_IVF256_Flat_nprobe_1.index")
    
    # 内部設定として固定 (UIからは隠蔽)
    rvc_source_path = def_rvc_source if def_rvc_source else "rvc_input.wav"
    rvc_output_path = def_rvc_output if def_rvc_output else "rvc_result.wav"

    if st.button("💾 Save Settings to JSON", use_container_width=True):
        new_config = {
            "gemini_api_key": gemini_key,
            "gcp_json_path": gcp_json_path,
            "rvc_model": rvc_model_path,
            "index_file": index_file,
            "rvc_source_path": rvc_source_path,
            "rvc_output_path": rvc_output_path
        }
        save_config(new_config)
        st.session_state["config"] = new_config
        st.success("Settings saved to config.json!")

# メインコンテンツ
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Input Dialogue")
    input_text = st.text_area("Japanese Text", placeholder="例：こんにちは、今日はいい天気ですね。", height=150)
    char_setting = st.text_input("Character Personality / Setting", placeholder="例：元気な女の子、クールな執事")
    
    st.subheader("2. Target Settings")
    target_lang = st.selectbox("Target Language", ["Japanese", "English", "French", "Spanish", "Chinese", "Korean", "German", "Italian"])
    
    lang_map = {
        "Japanese": "ja-JP", "English": "en-US", "French": "fr-FR", "Spanish": "es-ES",
        "Chinese": "zh-CN", "Korean": "ko-KR", "German": "de-DE", "Italian": "it-IT"
    }
    lang_code = lang_map[target_lang]
    
    if st.button("✨ Generate Base Audio", use_container_width=True):
        if not input_text:
            st.error("Textを入力してください。")
        elif not gemini_key or not gcp_json_path:
            st.error("API設定が不足しています（サイドバーを確認してください）。")
        else:
            with st.spinner("Processing..."):
                try:
                    os.environ["GEMINI_API_KEY"] = gemini_key
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcp_json_path
                    
                    translated = generate_multilingual_script(input_text, target_lang, char_setting)
                    st.session_state["translated_text"] = translated
                    
                    # TTS生成
                    # RVCの入力パス(rvc_source_path)に直接書き出す
                    output_file = rvc_source_path if rvc_source_path else "temp_output.mp3"
                    synthesize_multilingual_text(translated, lang_code, output_file=output_file)
                    st.session_state["output_file"] = output_file
                    
                    st.success("Generation Complete!")
                except Exception as e:
                    st.error(f"Error: {e}")

with col2:
    st.subheader("3. Results & Playback")
    
    # --- TTS Section ---
    st.write("#### 🔹 Base Audio (TTS)")
    if "translated_text" in st.session_state:
        st.info(f"**Translated Script ({target_lang}):**\n\n{st.session_state['translated_text']}")
        
        if "output_file" in st.session_state and os.path.exists(st.session_state["output_file"]):
            with open(st.session_state["output_file"], "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
            # Base audio download button removed
    else:
        st.write("翻訳・合成を実行するとここに表示されます。")

    st.divider()

    # --- RVC Result Section ---
    st.write("#### 👑 RVC Converted Voice")
    
    col_rvc1, col_rvc2 = st.columns([1, 1])
    with col_rvc1:
        if st.button("🚀 Run RVC Conversion", use_container_width=True, type="primary"):
            if not os.path.exists(rvc_source_path):
                st.error(f"Source file not found: {rvc_source_path}")
            elif not rvc_model_path:
                st.error("RVC Model Path is not set!")
            else:
                with st.spinner("Converting voice with RVC..."):
                    try:
                        from rvc_infer import run_rvc_conversion
                        # RVC-models ディレクトリを含むパスを解決
                        if "RVC-models" in rvc_model_path or os.path.isabs(rvc_model_path):
                            full_model_path = rvc_model_path
                        else:
                            full_model_path = os.path.join("RVC-models", rvc_model_path)
                        
                        success = run_rvc_conversion(
                            model_path=full_model_path,
                            input_path=rvc_source_path,
                            output_path=rvc_output_path,
                            pitch=0
                        )
                        if success:
                            st.success("RVC Conversion Complete!")
                        else:
                            st.error("RVC Conversion failed.")
                    except Exception as e:
                        st.error(f"RVC Error: {e}")

    # Reload RVC Output button removed as requested

    if rvc_output_path and os.path.exists(rvc_output_path):
        with open(rvc_output_path, "rb") as f:
            rvc_bytes = f.read()
        
        st.audio(rvc_bytes, format="audio/wav")
        
        # User can specify the filename before downloading
        save_filename = st.text_input("Name the Voice File", value=f"converted_voice_{target_lang}.wav")
        
        st.download_button(
            label="💾 Save Converted Voice",
            data=rvc_bytes,
            file_name=save_filename,
            mime="audio/wav",
            use_container_width=True
        )
    else:
        st.warning(f"RVC変換後のファイルが見つかりません: {rvc_output_path}")
        st.info("上のボタンを押してRVC変換を実行してください。")

st.markdown("---")
st.caption("RVCMultilingual App - Powered by Gemini & Google Cloud TTS")
