import os
import torch
from rvc_python.infer import RVCInference

# PyTorch 2.6+ セキュリティアップデート対策 (weights_only=True デフォルト化の回避)
# fairseq や RVC のモデルが読み込めなくなる現象を修正するモンキーパッチ
_original_load = torch.load
def _safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _safe_load


def run_rvc_conversion(model_path, input_path, output_path, pitch=0, device="cpu"):
    """
    rvc-python を用いて実際の音声変換（ボイスコンバート）を実行する関数。
    """
    try:
        # GPUが使える場合は自動的にcudaにする
        if device == "cpu" and torch.cuda.is_available():
            device = "cuda"

        print(f"Initializing RVC Inference on {device}...")
        rvc = RVCInference(device=device)

        print(f"Loading model: {model_path}")
        rvc.load_model(model_path)

        print(f"Converting: {input_path} (Pitch: {pitch})")
        
        # オプションパラメータ（必要に応じて調整可能）
        rvc.set_params(
            f0up_key=pitch,
            f0method="rmvpe", # 最も高品質なピッチ抽出アルゴリズム
            index_rate=0.75
        )

        # 変換実行
        rvc.infer_file(
            input_path=input_path,
            output_path=output_path
        )
        
        if os.path.exists(output_path):
            print("Conversion successful.")
            return True
        else:
            print("Output file was not created.")
            return False

    except Exception as e:
        print(f"RVC Inference Error: {e}")
        import traceback
        traceback.print_exc()
        return False

