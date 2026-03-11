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
        
        logger.info(f"RVC変換を実行します モデル: {model_path}")
        
        with _patch_torch_load():
            try:
                rvc = RVCInference(device=self._device)
                rvc.load_model(model_path)
                rvc.set_params(f0up_key=pitch, f0method=f0_method, index_rate=index_rate)
                rvc.infer_file(input_path=input_path, output_path=output_path)
            except Exception as e:
                logger.error(f"RVC推論中にエラーが発生: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
        
        if not os.path.exists(output_path):
            logger.error("出力ファイルが生成されませんでした。")
            return False
        
        if target_sr:
            resample_audio(output_path, target_sr)
        
        logger.info("RVC変換完了。")
        return True
