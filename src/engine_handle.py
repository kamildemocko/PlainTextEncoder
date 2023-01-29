from pathlib import Path

import chardet


def predict(path: Path, accuracy: int = 100) -> str:
    if not path.exists():
        raise FileNotFoundError

    with Path(path).open('rb') as f:
        # Join binary lines
        rawdata = b''.join([f.readline() for _ in range(accuracy)])

    return chardet.detect(rawdata)['encoding']


def convert_file(path: Path):
    if not path.exists():
        raise FileNotFoundError
