import streamlit as st
from core import setup_logging
from core.config import AppConfig
from ui.sidebar import render_sidebar
from ui.input_panel import render_input_panel
from ui.result_panel import render_result_panel

# ロギング設定の初期化
setup_logging()

st.set_page_config(page_title="Multi-language RVC Base Generator", layout="wide")
st.title("🌐 Multi-language RVC Base Generator")
st.markdown("Geminiで翻訳し、Google TTSで高品質なベース音声を生成します。")

# 設定の読み込み
if "config" not in st.session_state:
    st.session_state["config"] = AppConfig.load()

config = st.session_state["config"]

# UIの描画
config = render_sidebar(config)

col1, col2 = st.columns([1, 1])
with col1:
    render_input_panel(config)
with col2:
    render_result_panel(config)

st.markdown("---")
st.caption("RVCMultilingual App - Powered by Gemini & Google Cloud TTS")
