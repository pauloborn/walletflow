import os
import tempfile

from walletflow.dags.common_package.misc.Randomize import random_string


class TempWritableFile:
    file_path: str
    file_mode: str

    def __init__(self, file_prefix: str, mode: str = 'w'):
        dir_name = tempfile.gettempdirb()
        file_name = file_prefix + random_string(8)
        self.file_path = os.path.join(dir_name.decode(), file_name)
        self.file_mode = mode

    def __enter__(self):
        self.fd = open(self.file_path, self.file_mode)
        return self

    def __exit__(self, type, value, traceback):
        self.fd.close()

    def __del__(self):
        if not self.fd.closed:
            self.fd.close()
        os.remove(self.file_path)

    def write(self, s: str):
        self.fd.write(s)

    def flush(self):
        self.fd.flush()
