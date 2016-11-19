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
import sys
import tempfile
from   six   import add_metaclass

__all__ = ['InPlaceABC', 'InPlace', 'InPlaceBytes', 'DoubleOpenError']

class DoubleOpenError(Exception):
    pass

@add_metaclass(abc.ABCMeta)
class InPlaceABC(object):   ### TODO: Inherit one of the ABCs in `io`
    def __init__(self, filename, backup=None, backup_ext=None):
        #: The working directory at the time that the instance was created
        self._wd = os.getcwd()
        #: The name of the file to edit in-place
        self.filename = filename
        #: The absolute path of the file to edit in-place
        self.filepath = os.path.join(self._wd, filename)
        if backup is not None:
            #: The absolute path of the backup file (if any) that will be
            #: created after editing
            self.backup = os.path.join(self._wd, backup)
        elif backup_ext is not None and backup_ext != '':
            self.backup = self.filepath + backup_ext
        else:
            self.backup = None
        #: The input filehandle; only non-`None` while the instance is open
        self._infile = None
        #: The output filehandle; only non-`None` while the instance is open
        self._outfile = None
        #: The absolute path to the temporary file; only non-`None` while the
        #: instance is open
        self._tmppath = None
        #: Are we currently editing or trying to edit?
        self._open = False

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.rollback()
        else:
            self.close()
        return False

    def open(self):
        if not self._open:
            self._open = True
            try:
                fd, self._tmppath = tempfile.mkstemp(
                    dir=os.path.dirname(self.filepath),
                    prefix='._inplace-',
                )
                os.close(fd)
                copystats(self.filepath, self._tmppath) 
                self._infile = self._open_read(self.filepath)
                self._outfile = self._open_write(self._tmppath)
            except Exception:
                self.rollback()
                raise
        else:
            raise DoubleOpenError('open() called when file is already open')

    @abc.abstractmethod
    def _open_read(self, path):
        pass

    @abc.abstractmethod
    def _open_write(self, path):
        pass

    def _close(self):
        if self._infile is not None:
            self._infile.close()
            self._infile = None
        if self._outfile is not None:
            self._outfile.close()
            self._outfile = None

    def close(self):
        if self._open:
            self._open = False
            self._close()
            try:
                if self.backup is not None:
                    force_rename(self.filepath, self.backup)
                force_rename(self._tmppath, self.filepath)
            except EnvironmentError:
                try_unlink(self._tmppath)
                raise
            finally:
                self._tmppath = None
        ###else: error?

    def rollback(self):
        if self._open:
            self._open = False
            self._close()
            try_unlink(self._tmppath)
            self._tmppath = None
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
    def _open_read(self, path):
        return open(path, 'rb')

    def _open_write(self, path):
        return open(path, 'wb')


class InPlace(InPlaceABC):
    def __init__(self, filename, backup=None, backup_ext=None, encoding=None,
                 errors=None, newline=None):
        super(InPlace, self).__init__(filename, backup, backup_ext)
        self.encoding = encoding
        self.errors = errors
        self.newline = newline

    def _open_read(self, path):
        return io.open(path, 'rt', encoding=self.encoding, errors=self.errors,
                       newline=self.newline)

    def _open_write(self, path):
        return io.open(path, 'wt', encoding=self.encoding, errors=self.errors,
                       newline=self.newline)


def copystats(from_file, to_file):
    shutil.copystat(from_file, to_file)
    st = os.stat(from_file)
    # Based on GNU sed's behavior:
    try:
        os.chown(to_file, st.st_uid, st.st_gid)
    except EnvironmentError:
        try:
            os.chown(to_file, -1, st.st_gid)
        except EnvironmentError:
            pass

def force_rename(oldpath, newpath):
    if hasattr(os, 'replace'):  # Python 3.3+
        os.replace(oldpath, newpath)
    else:
        if sys.platform.startswith('win'):
            try_unlink(newpath)
        os.rename(oldpath, newpath)

def try_unlink(path):
    try:
        os.unlink(path)
    except EnvironmentError as e:
        if e.errno != ENOENT:
            raise
