import os
import torch
import torchaudio
from rvc_python.infer import RVCInference

# PyTorch 2.6+ セキュリティアップデート対策 (weights_only=True デフォルト化の回避)
# fairseq や RVC のモデルが読み込めなくなる現象を修正するモンキーパッチ
_original_load = torch.load
def _safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _safe_load

def resample_audio(file_path, target_sr=44100):
    """
    指定された音声ファイルを読み込み、目的のサンプリングレートに変換して保存し直します。
    """
    try:
        waveform, sample_rate = torchaudio.load(file_path)
        
        if sample_rate != target_sr:
            print(f"Resampling from {sample_rate}Hz to {target_sr}Hz...")
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)
            waveform_resampled = resampler(waveform)
            
            # 同じファイル名で上書き保存
            torchaudio.save(file_path, waveform_resampled, target_sr)
            print(f"Resampling complete. Audio is now {target_sr}Hz.")
        else:
            print(f"Audio is already {target_sr}Hz. No resampling needed.")
            
    except Exception as e:
        print(f"Resampling Error: {e}")

def run_rvc_conversion(model_path, input_path, output_path, pitch=0, device="cpu", target_sr=44100):
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
            
            # リサンプリング処理を追加
            if target_sr:
                resample_audio(output_path, target_sr)
                
            return True
        else:
            print("Output file was not created.")
            return False

    except Exception as e:
        print(f"RVC Inference Error: {e}")
        import traceback
        traceback.print_exc()
        return False
