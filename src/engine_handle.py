from pathlib import Path
from shutil import copy2
import threading

import chardet


def predict(path: Path, accuracy: int = 100) -> str:
    if not path.exists():
        raise FileNotFoundError

    with Path(path).open('rb') as f:
        # Join binary lines
        rawdata = b''.join([f.readline() for _ in range(accuracy)])

    return chardet.detect(rawdata)['encoding']


def convert_file(path: Path, encoding_in: str, encoding_out: str):
    def _convert_file():
        try:
            with backup_file.open(mode='rb') as fr, \
                    path.open(mode='wb') as fw:
                while True:
                    try:
                        txt = next(fr).decode(encoding_in, errors='ignore')
                        fw.write(txt.encode(encoding_out, errors='ignore'))
                    except StopIteration:
                        break

            backup_file.unlink()

        except UnicodeEncodeError:
            path.unlink()
            backup_file.rename(path)
            raise Exception('Unicode Encoding Error')

    if not path.exists():
        raise FileNotFoundError

    backup_file = Path(f'{path}.bak')
    copy2(path, backup_file)

    thread = threading.Thread(target=_convert_file)
    thread.start()
    thread.join()
