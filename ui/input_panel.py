import streamlit as st
from core.config import AppConfig
from core.constants import SUPPORTED_LANGUAGES, LANGUAGE_MAP
from core.pipeline import AudioPipeline

def render_input_panel(config: AppConfig):
    st.subheader("1. Input Dialogue")
    
    # セッションステートを使用して入力値を保持
    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""
    if "char_setting" not in st.session_state:
        st.session_state["char_setting"] = ""

    input_text = st.text_area("Japanese Text", value=st.session_state["input_text"], placeholder="例：こんにちは、今日はいい天気ですね。", height=150)
    char_setting = st.text_input("Character Personality / Setting", value=st.session_state["char_setting"], placeholder="例：元気な女の子、クールな執事")
    
    st.session_state["input_text"] = input_text
    st.session_state["char_setting"] = char_setting
    
    st.subheader("2. Target Settings")
    
    # セッションステートを使用して選択言語を保持
    if "target_lang" not in st.session_state:
        st.session_state["target_lang"] = SUPPORTED_LANGUAGES[0]
        
    target_lang = st.selectbox("Target Language", SUPPORTED_LANGUAGES, index=SUPPORTED_LANGUAGES.index(st.session_state["target_lang"]))
    st.session_state["target_lang"] = target_lang
    
    lang_code = LANGUAGE_MAP[target_lang]
    
    if st.button("✨ Generate Base Audio", use_container_width=True):
        if not input_text:
            st.error("Textを入力してください。")
        elif not config.gcp_json_path:
            st.error("GCPのAPI設定が不足しています（サイドバーを確認してください）。")
        else:
            with st.spinner("Processing..."):
                try:
                    pipeline = AudioPipeline(config)
                    translated, output_path = pipeline.translate_and_synthesize(
                        text=input_text,
                        target_lang=target_lang,
                        lang_code=lang_code,
                        character_setting=char_setting
                    )
                    
                    st.session_state["translated_text"] = translated
                    st.session_state["output_file"] = output_path
                    st.success("Generation Complete!")
                    
                except Exception as e:
                    st.error(f"Error: {e}")
