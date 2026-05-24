# RVCMultilingual リファクタリング提案書（実装済み）

## ✅ 現状（リファクタリング完了）

リファクタリングは完了しており、以下の構成が実際のフォルダ状況です。

### 現在のファイル構成

| ファイル / フォルダ | 行数 | 責務 |
|:---|:---:|:---|
| `app.py` | 32行 | Streamlitエントリポイント（薄いラッパー） |
| `main.py` | 53行 | CLIエントリポイント（薄いラッパー） |
| `requirements.txt` | 7行 | 依存パッケージ |
| `core/config.py` | 49行 | 設定管理クラス（一元化） |
| `core/constants.py` | 29行 | 定数定義（言語マップ、モデル名等） |
| `core/translator.py` | — | Gemini翻訳エンジン |
| `core/tts_engine.py` | — | Google Cloud TTS エンジン |
| `core/rvc_engine.py` | — | RVC変換エンジン |
| `core/audio_utils.py` | — | 音声ユーティリティ（リサンプリング等） |
| `core/pipeline.py` | — | パイプライン統合（翻訳→TTS→RVC） |
| `ui/sidebar.py` | — | サイドバーコンポーネント |
| `ui/input_panel.py` | — | 入力パネル |
| `ui/result_panel.py` | — | 結果表示パネル |

### 実装済みディレクトリ構成

```
RVCMultilingual/
├── app.py                    # Streamlitエントリポイント（薄いラッパー）✅
├── main.py                   # CLIエントリポイント（薄いラッパー）✅
├── requirements.txt          # 依存関係の明示 ✅
├── .env                      # シークレット管理（APIキー等）✅
├── config.json               # ユーザー設定（APIキー除外済み）✅
│
├── core/                     # ビジネスロジック層 ✅
│   ├── __init__.py           # ロギング設定
│   ├── config.py             # 設定管理クラス（一元化）
│   ├── constants.py          # 定数定義（言語マップ等）
│   ├── translator.py         # Gemini翻訳（gen_script.pyの後継）
│   ├── tts_engine.py         # Google Cloud TTS（tts_synth.pyの後継）
│   ├── rvc_engine.py         # RVC変換（rvc_infer.pyの後継）
│   ├── audio_utils.py        # 音声ユーティリティ（リサンプリング等）
│   └── pipeline.py           # パイプライン統合（翻訳→TTS→RVC）
│
├── ui/                       # Streamlit UI層 ✅
│   ├── sidebar.py            # サイドバーコンポーネント
│   ├── input_panel.py        # 入力パネル
│   └── result_panel.py       # 結果表示パネル
│
└── tests/                    # テスト（未実装）
```

---

## 📊 リファクタリング前の状態（参考）

### 旧ファイル構成

| ファイル | 行数 | 責務 |
|:---|:---:|:---|
| `app.py` | 187行 | Streamlit UI + ビジネスロジック（全責務が混在） |
| `rvc_infer.py` | 82行 | RVC音声変換 + リサンプリング |
| `tts_synth.py` | 44行 | Google Cloud TTS合成 |
| `gen_script.py` | 43行 | Gemini翻訳 |
| `main.py` | 33行 | CLI版エントリポイント（RVC変換機能なし） |
| `config.json` | 8行 | 設定ファイル（APIキー平文保存） |

### 解決済みの問題点

1. ✅ **`app.py`が肥大化** — `core/` と `ui/` に分離、187行→32行
2. ✅ **設定管理の散在** — `core/config.py` に一元化、APIキーは `.env` 管理
3. ✅ **定数のハードコーディング** — `core/constants.py` に集約
4. ✅ **モンキーパッチの恒久化** — `core/rvc_engine.py` でコンテキストマネージャ化
5. ✅ **`main.py`の形骸化** — RVC変換を含む完全なCLIとして実装
6. ✅ **`requirements.txt` の追加** — 依存関係を明示
7. ⚠️ **エラーハンドリングの統一** — ロギング基盤は導入済み、改善の余地あり
8. ❌ **テスト不能な構造** — `tests/` ディレクトリは未作成

---

## 📋 残タスク

| 優先度 | 項目 | 状態 |
|:---:|:---|:---:|
| 🟢 低 | テスト追加 (`tests/`) | ❌ 未着手 |
| 🟢 低 | `ui/__init__.py` の追加 | ❌ 未着手 |

---

## 🎯 リファクタリング効果（Before / After）

| 指標 | Before | After |
|:---|:---|:---|
| `app.py` の行数 | 187行（全責務混在） | 32行（UIのみ） |
| テスト可能性 | ❌ 不可 | ✅ 各モジュール独立テスト可能（テスト未作成） |
| 設定管理 | 3箇所に散在 | 1クラスに集約 |
| APIキー保護 | ⚠️ JSON平文保存 | 🔒 `.env`のみ |
| エラートレース | `print()` | 構造化ログ |
| 新言語追加 | UIファイル修正 | `constants.py`に1行追加 |
| CLI / GUI共用 | 部分的 | パイプラインクラスで完全共用 |