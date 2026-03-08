# RVC Multilingual Audio Generator

このアプリケーションは、Geminiによる多言語翻訳・台本生成、Google Cloud TTSによる基本音声の合成、および RVC (Retrieval-based Voice Conversion) を使用した声質変換を1つの画面で行えるStreamlitウェブアプリケーションです。

## 🚀 起動手順

1. **コマンドプロンプト（またはPowerShell）を開く**
   起動したい対象のフォルダ（`d:\AntiGravity\RVCMultilingual`）をカレントディレクトリにします。
   
   ```bash
   cd d:\AntiGravity\RVCMultilingual
   ```

2. **仮想環境の有効化（必要な場合）**
   Pythonの仮想環境（`venv`）を利用している場合は有効化します。

   ```bash
   .\venv\Scripts\activate
   ```

3. **アプリケーションの起動**
   以下のコマンドを実行してStreamlitアプリを起動します。

   ```bash
   streamlit run app.py
   ```
   ※仮想環境から直接実行する場合は `.\venv\Scripts\streamlit run app.py` としても起動できます。

4. **ブラウザで開く**
   コマンドを実行すると、自動的に標準のWebブラウザが立ち上がり、アプリケーションの画面（通常は `http://localhost:8501` ）が表示されます。自動で開かない場合は、ターミナルに表示されているURLをブラウザに手動でコピー＆ペーストしてください。

---

## 🛑 終了手順

アプリケーション（サーバー）を終了するには、起動したコマンドプロンプト（ターミナル）画面で以下の操作を行います。

1. コマンドプロンプトのウィンドウを選択してアクティブにします。
2. キーボードの **`Ctrl` キー を押しながら `C` キー** を押します。（`Ctrl + C`）
3. サーバーが安全にシャットダウンされ、通常のコマンド入力待機状態に戻ります。
4. （仮想環境を有効化していた場合は、`deactivate` と入力してエンターを押すと仮想環境から抜けられます。）
5. アプリケーションを開いていたブラウザのタブは、そのまま閉じて構いません。

---

## 💡 基本的な使い方

1. 左サイドバーの設定画面（⚙️ Settings / 🎙️ RVC Settings）で必要なAPIキー（Gemini, GCP）や使用するRVCモデル名を入力し、設定を保存します。
2. メイン画面の「1. Input Dialogue」で喋らせたい日本語のテキストとキャラクター設定を入力します。
3. 「2. Target Settings」で翻訳して喋らせたいターゲット言語を選択します。
4. 「**Generate Script & Base Audio**」ボタンを押すと、翻訳とGoogle TTSによるベース音声が生成されます。
5. 「3. Results & Playback」にベース音声が表示されるので、再生してイントネーション等を確認します。
6. 「**🚀 Run RVC Conversion**」ボタンを押すと、ローカルのRVCモデルを使用して声質が変換されます。
7. 変換が完了したら「**💾 Save Converted Voice**」ボタンを押して、お使いの環境に音声ファイル（WAV形式）を保存します。保存する際のファイル名は自由に設定可能です。
