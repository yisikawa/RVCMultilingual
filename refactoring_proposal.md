# RVCMultilingual リファクタリング提案書

## 📊 現状の分析

### ファイル構成

| ファイル | 行数 | 責務 |
|:---|:---:|:---|
| `app.py` | 187行 | Streamlit UI + ビジネスロジック（全責務が混在） |
| `rvc_infer.py` | 82行 | RVC音声変換 + リサンプリング |
| `tts_synth.py` | 44行 | Google Cloud TTS合成 |
| `gen_script.py` | 43行 | Gemini翻訳 |
| `main.py` | 33行 | CLI版エントリポイント |
| `config.json` | 8行 | 設定ファイル |

### 主な問題点

> [!WARNING]
> **セキュリティリスク**: `config.json`にAPIキーが平文で保存されており、`.gitignore`に含まれているものの、流出リスクがあります。

1. **`app.py`が肥大化** — UI表示、設定管理、ビジネスロジック（翻訳→TTS→RVC）がすべて1ファイル187行に詰め込まれている
2. **設定管理の散在** — `.env`、`config.json`、`os.environ`への直接書き込みが混在し、設定の流れが不明瞭
3. **エラーハンドリングが不統一** — `print()`でのログ出力と`st.error()`が混在。ロギング機構がない
4. **定数のハードコーディング** — 言語マップ、デフォルトパス、Geminiモデル名などが各所に散らばっている
5. **型安全性の欠如** — 型ヒント未使用、引数の検証なし
6. **テスト不能な構造** — UIとロジックが密結合のためユニットテスト困難
7. **モンキーパッチの恒久化** — `torch.load`のオーバーライドがモジュールレベルで実行され副作用が大きい
8. **`main.py`の形骸化** — CLIエントリポイントがあるがRVC変換機能が含まれておらず、実質未使用

---

## 🏗️ 提案するディレクトリ構成

```
RVCMultilingual/
├── app.py                    # Streamlitエントリポイント（薄いラッパー）
├── main.py                   # CLIエントリポイント（薄いラッパー）
├── config.json               # ユーザー設定（API キー除外推奨）
├── .env                      # シークレット管理（APIキー等）
├── requirements.txt          # 依存関係の明示
│
├── core/                     # ビジネスロジック層
│   ├── __init__.py
│   ├── config.py             # 設定管理クラス（一元化）
│   ├── constants.py          # 定数定義（言語マップ等）
│   ├── translator.py         # Gemini翻訳（gen_script.pyの後継）
│   ├── tts_engine.py         # Google Cloud TTS（tts_synth.pyの後継）
│   ├── rvc_engine.py         # RVC変換（rvc_infer.pyの後継）
│   ├── audio_utils.py        # 音声ユーティリティ（リサンプリング等）
│   └── pipeline.py           # パイプライン統合（翻訳→TTS→RVC）
│
├── ui/                       # Streamlit UI層
│   ├── __init__.py
│   ├── sidebar.py            # サイドバーコンポーネント
│   ├── input_panel.py        # 入力パネル
│   └── result_panel.py       # 結果表示パネル
│
├── tests/                    # テスト
│   ├── __init__.py
│   ├── test_translator.py
│   ├── test_tts_engine.py
│   ├── test_rvc_engine.py
│   └── test_pipeline.py
│
└── models/                   # RVCモデルファイル（.gitignore対象）
```

---

## 🔧 各リファクタリング項目の詳細

### 1. 設定管理の一元化 (`core/config.py`)

**現状の問題**: `.env`、`config.json`、`os.environ`への動的書き込みが混在

```python
# core/config.py
from dataclasses import dataclass, field
from pathlib import Path
import json
import os
from dotenv import load_dotenv

@dataclass
class AppConfig:
    """アプリケーション設定を一元管理するクラス"""
    # シークレット（.envから読み込み、config.jsonには保存しない）
    gemini_api_key: str = ""
    gcp_json_path: str = ""
    
    # RVC設定
    rvc_model: str = ""
    index_file: str = ""
    rvc_source_path: str = "rvc_input.wav"
    rvc_output_path: str = "rvc_result.wav"
    
    @classmethod
    def load(cls, config_path: str = "config.json") -> "AppConfig":
        """設定ファイルと環境変数から設定を読み込む"""
        load_dotenv()
        config_data = {}
        if Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        
        return cls(
            gemini_api_key=config_data.get("gemini_api_key", os.getenv("GEMINI_API_KEY", "")),
            gcp_json_path=config_data.get("gcp_json_path", os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")),
            rvc_model=config_data.get("rvc_model", ""),
            index_file=config_data.get("index_file", ""),
            rvc_source_path=config_data.get("rvc_source_path", "rvc_input.wav"),
            rvc_output_path=config_data.get("rvc_output_path", "rvc_result.wav"),
        )
    
    def save(self, config_path: str = "config.json") -> None:
        """設定をJSONファイルに保存する"""
        data = {
            "rvc_model": self.rvc_model,
            "index_file": self.index_file,
            "rvc_source_path": self.rvc_source_path,
            "rvc_output_path": self.rvc_output_path,
            # 注意: APIキーは保存しない（.envで管理推奨）
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
```

> [!IMPORTANT]
> **APIキーの管理方針**: `config.json`からAPIキーを除外し、`.env`ファイルのみでシークレットを管理する運用を推奨します。現状は`config.json`にAPIキーが平文保存されています。

---

### 2. 定数の集約 (`core/constants.py`)

**現状の問題**: 言語マップ、デフォルト値がUIファイル内にハードコーディング

```python
# core/constants.py

# 対応言語マップ（表示名 → BCP-47コード）
LANGUAGE_MAP: dict[str, str] = {
    "Japanese": "ja-JP",
    "English": "en-US",
    "French": "fr-FR",
    "Spanish": "es-ES",
    "Chinese": "zh-CN",
    "Korean": "ko-KR",
    "German": "de-DE",
    "Italian": "it-IT",
}

# サポートする言語の一覧
SUPPORTED_LANGUAGES: list[str] = list(LANGUAGE_MAP.keys())

# Geminiモデル名
GEMINI_MODEL_NAME: str = "gemini-2.0-flash"

# RVCデフォルト設定
DEFAULT_PITCH: int = 0
DEFAULT_F0_METHOD: str = "rmvpe"
DEFAULT_INDEX_RATE: float = 0.75
DEFAULT_TARGET_SR: int = 44100

# デフォルト音声パス
DEFAULT_RVC_INPUT: str = "rvc_input.wav"
DEFAULT_RVC_OUTPUT: str = "rvc_result.wav"
```

---

### 3. ビジネスロジックの分離

#### 3a. 翻訳エンジン (`core/translator.py`)

`gen_script.py`の後継。API設定の依存注入パターンを導入。

```python
# core/translator.py
import google.generativeai as genai
from core.constants import GEMINI_MODEL_NAME

class GeminiTranslator:
    """Gemini APIによる多言語翻訳クラス"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini APIキーが設定されていません")
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    def translate(self, text: str, target_lang: str, character_setting: str = "") -> str:
        """テキストをターゲット言語に翻訳する"""
        prompt = self._build_prompt(text, target_lang, character_setting)
        response = self._model.generate_content(prompt)
        return response.text.strip()
    
    @staticmethod
    def _build_prompt(text: str, target_lang: str, character_setting: str) -> str:
        """翻訳プロンプトを構築する"""
        return f"""以下のテキストを{target_lang}に翻訳してください。

テキスト: {text}
設定: {character_setting}

要件:
1. 自然な話し言葉であること。
2. 音声合成（TTS）に適した形式であること。
3. 設定がある場合は、そのキャラクターらしい口調にすること。

出力は翻訳後のテキストのみにしてください。"""
```

#### 3b. 音声ユーティリティ分離 (`core/audio_utils.py`)

リサンプリング等の汎用処理を独立モジュール化。

```python
# core/audio_utils.py
import logging
import torchaudio
from core.constants import DEFAULT_TARGET_SR

logger = logging.getLogger(__name__)

def resample_audio(file_path: str, target_sr: int = DEFAULT_TARGET_SR) -> None:
    """音声ファイルを指定サンプリングレートに変換する"""
    waveform, sample_rate = torchaudio.load(file_path)
    
    if sample_rate == target_sr:
        logger.info(f"音声は既に {target_sr}Hz です。リサンプリング不要。")
        return
    
    logger.info(f"{sample_rate}Hz → {target_sr}Hz にリサンプリング中...")
    resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)
    waveform_resampled = resampler(waveform)
    torchaudio.save(file_path, waveform_resampled, target_sr)
    logger.info("リサンプリング完了。")
```

#### 3c. RVCエンジン (`core/rvc_engine.py`)

モンキーパッチのスコープを制限し、クラスとして管理。

```python
# core/rvc_engine.py
import os
import logging
import torch
from contextlib import contextmanager
from rvc_python.infer import RVCInference
from core.audio_utils import resample_audio
from core.constants import DEFAULT_PITCH, DEFAULT_F0_METHOD, DEFAULT_INDEX_RATE, DEFAULT_TARGET_SR

logger = logging.getLogger(__name__)

@contextmanager
def _patch_torch_load():
    """torch.loadのweights_only制限を一時的に緩和するコンテキストマネージャ"""
    original_load = torch.load
    def _safe_load(*args, **kwargs):
        kwargs['weights_only'] = False
        return original_load(*args, **kwargs)
    torch.load = _safe_load
    try:
        yield
    finally:
        torch.load = original_load

class RVCEngine:
    """RVC音声変換エンジン"""
    
    def __init__(self, device: str = "auto"):
        if device == "auto":
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self._device = device
        logger.info(f"RVCデバイス: {self._device}")
    
    def convert(
        self,
        model_path: str,
        input_path: str,
        output_path: str,
        pitch: int = DEFAULT_PITCH,
        f0_method: str = DEFAULT_F0_METHOD,
        index_rate: float = DEFAULT_INDEX_RATE,
        target_sr: int | None = DEFAULT_TARGET_SR,
    ) -> bool:
        """音声変換を実行する"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"入力ファイルが見つかりません: {input_path}")
        
        with _patch_torch_load():
            rvc = RVCInference(device=self._device)
            rvc.load_model(model_path)
            rvc.set_params(f0up_key=pitch, f0method=f0_method, index_rate=index_rate)
            rvc.infer_file(input_path=input_path, output_path=output_path)
        
        if not os.path.exists(output_path):
            logger.error("出力ファイルが生成されませんでした。")
            return False
        
        if target_sr:
            resample_audio(output_path, target_sr)
        
        logger.info("RVC変換完了。")
        return True
```

> [!TIP]
> `torch.load`のモンキーパッチを**コンテキストマネージャ**で囲むことで、影響範囲をRVC推論時のみに限定できます。現状ではモジュール読み込み時にグローバルに適用されており、他のライブラリに予期しない副作用を与える可能性があります。

---

### 4. パイプライン統合 (`core/pipeline.py`)

翻訳→TTS→RVCの一連のフローを統合するオーケストレーター。

```python
# core/pipeline.py
import logging
from core.config import AppConfig
from core.translator import GeminiTranslator
from core.tts_engine import TTSEngine
from core.rvc_engine import RVCEngine

logger = logging.getLogger(__name__)

class AudioPipeline:
    """翻訳→TTS→RVC変換のパイプライン"""
    
    def __init__(self, config: AppConfig):
        self._config = config
        self._translator = GeminiTranslator(config.gemini_api_key)
        self._tts = TTSEngine(config.gcp_json_path)
        self._rvc = RVCEngine()
    
    def translate_and_synthesize(
        self, text: str, target_lang: str, lang_code: str, character_setting: str = ""
    ) -> tuple[str, str]:
        """翻訳とTTS合成を実行し、(翻訳テキスト, 出力ファイルパス)を返す"""
        translated = self._translator.translate(text, target_lang, character_setting)
        output_path = self._config.rvc_source_path
        self._tts.synthesize(translated, lang_code, output_file=output_path)
        return translated, output_path
    
    def run_rvc_conversion(self) -> bool:
        """RVC変換を実行する"""
        model_path = self._resolve_model_path(self._config.rvc_model)
        return self._rvc.convert(
            model_path=model_path,
            input_path=self._config.rvc_source_path,
            output_path=self._config.rvc_output_path,
        )
    
    def _resolve_model_path(self, model_path: str) -> str:
        """モデルパスを解決する"""
        import os
        if os.path.exists(model_path) or os.path.isabs(model_path):
            return model_path
        return os.path.join("RVC-models", model_path)
```

---

### 5. UI層の分離 (`ui/`)

`app.py`をUIのみの薄いラッパーにリファクタリング。

```python
# app.py（リファクタリング後、約30行）
import streamlit as st
from core.config import AppConfig
from ui.sidebar import render_sidebar
from ui.input_panel import render_input_panel
from ui.result_panel import render_result_panel

st.set_page_config(page_title="Multi-language RVC Base Generator", layout="wide")
st.title("🌐 Multi-language RVC Base Generator")
st.markdown("Geminiで翻訳し、Google TTSで高品質なベース音声を生成します。")

config = render_sidebar()

col1, col2 = st.columns([1, 1])
with col1:
    render_input_panel(config)
with col2:
    render_result_panel(config)

st.markdown("---")
st.caption("RVCMultilingual App - Powered by Gemini & Google Cloud TTS")
```

---

### 6. ロギング基盤の導入

**現状の問題**: `print()`とStreamlitの`st.error()`が混在

```python
# core/__init__.py
import logging

def setup_logging(level: int = logging.INFO) -> None:
    """アプリケーション全体のロギングを設定する"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log", encoding="utf-8"),
        ],
    )
```

---

### 7. `requirements.txt` の追加

依存関係が明示されていないため、追加を推奨。

```
streamlit>=1.30.0
google-generativeai>=0.3.0
google-cloud-texttospeech>=2.14.0
torch>=2.0.0
torchaudio>=2.0.0
rvc-python>=0.1.0
python-dotenv>=1.0.0
```

---

## 📋 実施優先度

| 優先度 | 項目 | 理由 | 工数目安 |
|:---:|:---|:---|:---:|
| 🔴 高 | セキュリティ改善（APIキー管理） | 情報漏洩リスク | 30分 |
| 🔴 高 | 設定管理の一元化 (`core/config.py`) | 他リファクタの基盤 | 1時間 |
| 🟡 中 | 定数集約 (`core/constants.py`) | 保守性向上 | 30分 |
| 🟡 中 | ビジネスロジック分離 (`core/`) | テスタビリティ向上 | 2時間 |
| 🟡 中 | パイプライン統合 (`core/pipeline.py`) | 再利用性向上 | 1時間 |
| 🟡 中 | UI層の分離 (`ui/`) | `app.py`の可読性改善 | 1.5時間 |
| 🟢 低 | ロギング基盤導入 | 運用・デバッグ改善 | 30分 |
| 🟢 低 | `requirements.txt` 追加 | 環境再現性 | 15分 |
| 🟢 低 | テスト追加 (`tests/`) | 品質保証 | 2時間 |

**推定合計工数**: 約 **8〜9時間**

---

## 🎯 期待される効果

| 指標 | Before | After |
|:---|:---|:---|
| `app.py` の行数 | 187行（全責務混在） | 約30行（UIのみ） |
| テスト可能性 | ❌ 不可 | ✅ 各モジュール独立テスト可能 |
| 設定管理 | 3箇所に散在 | 1クラスに集約 |
| APIキー保護 | ⚠️ JSON平文保存 | 🔒 `.env`のみ |
| エラートレース | `print()` | 構造化ログ |
| 新言語追加 | UIファイル修正 | `constants.py`に1行追加 |
| CLI / GUI共用 | 部分的 | パイプラインクラスで完全共用 |

---

## ⚡ クイックスタート（段階的導入の推奨手順）

既存の動作を壊さずに段階的に導入する手順です：

1. **Phase 1**: `core/constants.py` と `core/config.py` を作成し、既存コードから参照
2. **Phase 2**: `gen_script.py` → `core/translator.py`、`tts_synth.py` → `core/tts_engine.py` に移行（旧ファイルは薄いラッパーとして残す）
3. **Phase 3**: `rvc_infer.py` → `core/rvc_engine.py` + `core/audio_utils.py` に分離
4. **Phase 4**: `core/pipeline.py` を作成し、`app.py` と `main.py` を薄いラッパー化
5. **Phase 5**: `ui/` ディレクトリにStreamlitコンポーネントを分離
6. **Phase 6**: テスト追加、旧ファイルの削除
