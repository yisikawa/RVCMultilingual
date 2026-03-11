import os
import streamlit as st
from core.config import AppConfig
from core.pipeline import AudioPipeline

def render_result_panel(config: AppConfig):
    st.subheader("3. Results & Playback")
    
    # --- TTS Section ---
    st.write("#### 🔹 Base Audio (TTS)")
    if "translated_text" in st.session_state:
        st.info(f"**Translated Script ({st.session_state.get('target_lang', 'Unknown')}):**\n\n{st.session_state['translated_text']}")
        
        output_file = st.session_state.get("output_file")
        if output_file and os.path.exists(output_file):
            with open(output_file, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
    else:
        st.write("翻訳・合成を実行するとここに表示されます。")

    st.divider()

    # --- RVC Result Section ---
    st.write("#### 👑 RVC Converted Voice")
    
    col_rvc1, col_rvc2 = st.columns([1, 1])
    with col_rvc1:
        if st.button("🚀 Run RVC Conversion", use_container_width=True, type="primary"):
            if not os.path.exists(config.rvc_source_path):
                st.error(f"Source file not found: {config.rvc_source_path}")
            elif not config.rvc_model:
                st.error("RVC Model Path is not set!")
            else:
                with st.spinner("Converting voice with RVC..."):
                    try:
                        pipeline = AudioPipeline(config)
                        success = pipeline.run_rvc_conversion()
                        
                        if success:
                            st.success("RVC Conversion Complete!")
                        else:
                            st.error("RVC Conversion failed.")
                    except Exception as e:
                        st.error(f"RVC Error: {e}")

    if config.rvc_output_path and os.path.exists(config.rvc_output_path):
        with open(config.rvc_output_path, "rb") as f:
            rvc_bytes = f.read()
        
        st.audio(rvc_bytes, format="audio/wav")
        
        target_lang = st.session_state.get('target_lang', 'unknown')
        save_filename = st.text_input("Name the Voice File", value=f"converted_voice_{target_lang}.wav")
        
        st.download_button(
            label="💾 Save Converted Voice",
            data=rvc_bytes,
            file_name=save_filename,
            mime="audio/wav",
            use_container_width=True
        )
    else:
        st.warning(f"RVC変換後のファイルが見つかりません: {config.rvc_output_path}")
        st.info("上のボタンを押してRVC変換を実行してください。")
