import logging
import torchaudio
from core.constants import DEFAULT_TARGET_SR

logger = logging.getLogger(__name__)

def resample_audio(file_path: str, target_sr: int = DEFAULT_TARGET_SR) -> None:
    """音声ファイルを指定サンプリングレートに変換する"""
    try:
        waveform, sample_rate = torchaudio.load(file_path)
        
        if sample_rate == target_sr:
            logger.info(f"音声は既に {target_sr}Hz です。リサンプリング不要。")
            return
        
        logger.info(f"{sample_rate}Hz → {target_sr}Hz にリサンプリング中...")
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)
        waveform_resampled = resampler(waveform)
        torchaudio.save(file_path, waveform_resampled, target_sr)
        logger.info("リサンプリング完了。")
        
    except Exception as e:
        logger.error(f"リサンプリングエラー: {e}")
        raise
