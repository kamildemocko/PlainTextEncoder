import sys
from pathlib import Path

import chardet


def predict_encoding(file_path: Path, n_lines: int = 20) -> str:
    '''Predict a file's encoding using chardet'''

    # Open the file as binary data
    with Path(file_path).open('rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']


if __name__ == '__main__':

    if len(sys.argv) < 2:
      print("usage: <script> <path>")
      sys.exit()

    _file = Path(sys.argv[1]).resolve()
    _file_enc = predict_encoding(_file, n_lines=100)
    _new_file = _file.parent.joinpath(f"enc {_file.name}")

    if _file_enc == 'UTF-8-SIG':
      raise AssertionError('Already UTF-8-SIG')

    print(f'Convereting from {_file_enc.upper()} to UTF-8-SIG')
    with _file.open('r', encoding=_file_enc) as fr, _new_file.open('w', encoding='UTF-8-SIG') as fw:
      while True:
        try:
          fw.write(next(fr))
        except StopIteration:
          break
      print('Encoded file written')
