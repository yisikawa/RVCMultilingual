import logging
import torch
import torchaudio
import soundfile as sf
from core.constants import DEFAULT_TARGET_SR

logger = logging.getLogger(__name__)

def resample_audio(file_path: str, target_sr: int = DEFAULT_TARGET_SR) -> None:
    """音声ファイルを指定サンプリングレートに変換する"""
    try:
        # soundfileで直接読み込み（torchaudioのバックエンド問題を回避）
        data, sample_rate = sf.read(file_path, always_2d=True)

        if sample_rate == target_sr:
            return

        waveform = torch.FloatTensor(data.T)
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_sr)
        waveform_resampled = resampler(waveform)
        sf.write(file_path, waveform_resampled.numpy().T, target_sr)

    except Exception as e:
        logger.warning(f"リサンプリングをスキップしました（変換済みファイルはそのまま使用）: {e}")