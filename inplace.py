# Benefits: lets you specify the complete filename of the backup file, not just
# an extension; lets you control the encoding; doesn't redirect stdout; `read`
# method

# cf. <https://hg.python.org/cpython/file/2.7/Lib/fileinput.py#l310>

from   contextlib import contextmanager
from   errno      import ENOENT
import os
import os.path

@contextmanager
def ignore_enoent():
    try:
        yield
    except EnvironmentError as e:
        if e.errno != ENOENT
            raise

class InPlace(object):   ### Inherit one of the ABCs in `io`
    def __init__(self, filename, backup=None, backup_ext=None):
        self.filename = filename
        if backup is not None:
            self.backup = backup
        elif backup_ext is not None:
            self.backup = filename + backup_ext
        else:
            self.backup = None
        self._wd = os.getcwd()
        self._editing = False
        self._infile = None
        self._outfile = None

    def __enter__(self):
        self._editing = True
        if self.backup is not None:
            self._backup_path = os.path.join(self._wd, self.backup)
        else:
            self._backup_path = os.path.join(self._wd, ??? )
        os.rename(os.path.join(self._wd, self.filename), self._backup_path)
        ### Open filehandles
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._infile.close()
        self._outfile.close()
        if exc_type is not None:
            ### Delete new file and replace with backup file
        elif self.backup is None:
            with ignore_enoent():
                os.unlink(self._backup_path)
        self._editing = False
        return False

    def read(self, size=-1):
        return self._infile.read(size)

    def readline(self, size=-1):
        return self._infile.readline(size)

    def readlines(self, sizehint=-1):
        return self._infile.readlines(sizehint)

    def write(self, s):
        self._outfile.write(s)

    def writelines(self, seq):
        self._outfile.writelines(seq)

    def __iter__(self):
        return iter(self._infile)

    def open
    def close
    def flush
    def readinto  ### for binary streams, at least
