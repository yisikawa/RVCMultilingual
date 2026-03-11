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
