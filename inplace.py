__version__ = '0.1.0.dev1'

# Benefits: lets you specify the complete filename of the backup file, not just
# an extension; lets you control the encoding; doesn't redirect stdout; `read`
# method

# cf. <https://hg.python.org/cpython/file/2.7/Lib/fileinput.py#l310>

from   contextlib import contextmanager
from   errno      import ENOENT
import os
import os.path
import shutil
import tempfile

@contextmanager
def ignore_enoent():
    try:
        yield
    except EnvironmentError as e:
        if e.errno != ENOENT:
            raise

class InPlace(object):   ### TODO: Inherit one of the ABCs in `io`
    def __init__(self, filename, backup=None, backup_ext=None):
        self._wd = os.getcwd()
        self.filename = filename
        self.filepath = os.path.join(self._wd, filename)
        if backup is not None:
            self.backup = os.path.join(self._wd, backup)
        elif backup_ext is not None:
            self.backup = self.filepath + backup_ext
        else:
            self.backup = None
        self._infile = None
        self._outfile = None
        self._backup_path = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.discard()
        else:
            self.close()
        return False

    def open(self):
        if self._infile is None:
            if self.backup is not None:
                self._backup_path = self.backup
            else:
                fd, tmppath = tempfile.mkstemp(prefix='inplace')
                os.close(fd)
                self._backup_path = tmppath
            shutil.copyfile(self.filepath, self._backup_path)
            shutil.copystat(self.filepath, self._backup_path)
            self._infile = open(self._backup_path, 'r')
            self._outfile = open(self.filepath, 'w')
        #else: error?

    def _close(self):
        self._infile.close()
        self._outfile.close()
        self._infile = None
        self._outfile = None

    def close(self):
        if self._infile is not None:
            self._close()
            if self.backup is None:
                with ignore_enoent():
                    os.unlink(self._backup_path)
        #else: error?

    def discard(self):
        if self._infile is not None:
            self._close()
            shutil.copyfile(self._backup_path, self.filepath)
        #else: error?

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
