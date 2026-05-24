import streamlit as st
from core.config import AppConfig

def render_sidebar(config: AppConfig) -> AppConfig:
    with st.sidebar:
        st.header("⚙️ API & Model Settings")
        
        gcp_json_path = st.text_input("GCP Service Account JSON Path", value=config.gcp_json_path)
        
        st.divider()
        st.header("🎙️ RVC Settings")
        rvc_model_path = st.text_input("RVC Model Name / Path", value=config.rvc_model, placeholder="e.g. haruka_v2.pth")
        index_file = st.text_input("Index File Path", value=config.index_file, placeholder="e.g. added_IVF256_Flat_nprobe_1.index")
        
        if st.button("💾 Save Settings to JSON", use_container_width=True):
            config.gcp_json_path = gcp_json_path
            config.rvc_model = rvc_model_path
            config.index_file = index_file
            config.save()
            st.success("Settings saved successfully!")
            
    # UI上の変更を反映させる
    config.gcp_json_path = gcp_json_path
    config.rvc_model = rvc_model_path
    config.index_file = index_file
    
    return config
