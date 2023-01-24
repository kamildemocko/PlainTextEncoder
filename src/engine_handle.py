from pathlib import Path

from src.engine import predict_encoding


def predict(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError

    return predict_encoding(path)

