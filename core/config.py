from dataclasses import dataclass
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
            gemini_api_key=config_data.get("gemini_api_key") or os.getenv("GEMINI_API_KEY", ""),
            gcp_json_path=config_data.get("gcp_json_path") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
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
