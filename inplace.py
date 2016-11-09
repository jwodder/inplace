__version__      = '0.1.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'inplace@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/inplace'

import abc
from   errno import ENOENT
import io
import os
import os.path
import shutil
import tempfile

class InPlaceABC(object):   ### TODO: Inherit one of the ABCs in `io`
    def __init__(self, filename, backup=None, backup_ext=None):
        self._wd = os.getcwd()
        self.filename = filename
        self.filepath = os.path.join(self._wd, filename)
        if backup is not None:
            self.backup = os.path.join(self._wd, backup)
        elif backup_ext is not None and backup_ext != '':
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

    @abc.abstractmethod
    def open(self):
        pass

    def _close(self):
        self._infile.close()
        self._outfile.close()
        self._infile = None
        self._outfile = None

    def close(self):
        if self._infile is not None:
            self._close()
            if self.backup is None:
                try:
                    os.unlink(self._backup_path)
                except EnvironmentError as e:
                    if e.errno != ENOENT:
                        raise
        ###else: error?

    def discard(self):
        if self._infile is not None:
            self._close()
            shutil.copyfile(self._backup_path, self.filepath)
        ###else: error?

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


class InPlaceBytes(InPlaceABC):
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
            self._infile = open(self._backup_path, 'rb')
            self._outfile = open(self.filepath, 'wb')
        ###else: error?


class InPlace(InPlaceABC):
    def __init__(self, filename, backup=None, backup_ext=None, encoding=None,
                 errors=None, newline=None):
        super(InPlace, self).__init__(filename, backup, backup_ext)
        self.encoding = encoding
        self.errors = errors
        self.newline = newline

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
            self._infile = io.open(
                self._backup_path,
                'rt',
                encoding=self.encoding,
                errors=self.errors,
                newline=self.newline,
            )
            self._outfile = io.open(
                self.filepath,
                'wt',
                encoding=self.encoding,
                errors=self.errors,
                newline=self.newline,
            )
        ###else: error?
