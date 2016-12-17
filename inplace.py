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
class InPlaceABC(object):
    UNOPENED = 0
    OPEN = 1
    CLOSED = 2

    def __init__(self, name, backup=None, backup_ext=None, delay_open=False,
                 move_first=False):
        cwd = os.getcwd()
        #: The name of the file to edit in-place
        self.name = name
        #: The absolute path of the file to edit in-place
        self.filepath = os.path.join(cwd, name)
        if backup is not None:
            #: The absolute path of the backup file (if any) that will be
            #: created after editing
            self.backuppath = os.path.join(cwd, backup)
        elif backup_ext is not None and backup_ext != '':
            self.backuppath = self.filepath + backup_ext
        else:
            self.backuppath = None
        self.move_first = move_first
        #: The input filehandle; only non-`None` while the instance is open
        self.input = None
        #: The output filehandle; only non-`None` while the instance is open
        self.output = None
        #: The absolute path to the temporary file; only non-`None` while the
        #: instance is open
        self._tmppath = None
        #: Are we not open yet, open, or closed?
        self._state = self.UNOPENED
        if not delay_open:
            self.open()

    def __enter__(self):
        if self._state < self.OPEN:
            self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._state == self.OPEN:
            if exc_type is not None:
                self.rollback()
            else:
                self.close()
        return False

    def mktemp(self, filepath):
        fd, tmppath = tempfile.mkstemp(
            dir=os.path.dirname(filepath),
            prefix='._inplace-',
        )
        os.close(fd)
        return tmppath

    def open(self):
        if self._state < self.OPEN:
            self._state = self.OPEN
            try:
                if self.move_first:
                    if self.backuppath is not None:
                        self._tmppath = self.mktemp(self.backuppath)
                    else:
                        self._tmppath = self.mktemp(self.filepath)
                    force_rename(self.filepath, self._tmppath)
                    self.input = self._open_read(self._tmppath)
                    self.output = self._open_write(self.filepath)
                    copystats(self._tmppath, self.filepath)
                else:
                    self._tmppath = self.mktemp(self.filepath)
                    copystats(self.filepath, self._tmppath) 
                    self.input = self._open_read(self.filepath)
                    self.output = self._open_write(self._tmppath)
            except Exception:
                self.rollback()
                raise
        else:
            raise DoubleOpenError('open() called twice on same filehandle')

    @abc.abstractmethod
    def _open_read(self, path):
        pass

    @abc.abstractmethod
    def _open_write(self, path):
        pass

    def _close(self):
        if self.input is not None:
            self.input.close()
            self.input = None
        if self.output is not None:
            self.output.close()
            self.output = None

    def close(self):
        if self._state == self.UNOPENED:
            raise ValueError('Cannot close unopened file')
        elif self._state == self.OPEN:
            self._state = self.CLOSED
            self._close()
            try:
                if self.move_first:
                    if self.backuppath is not None:
                        force_rename(self._tmppath, self.backuppath)
                        ### Delete tempfile on error?
                    else:
                        try_unlink(self._tmppath)
                else:
                    try:
                        if self.backuppath is not None:
                            force_rename(self.filepath, self.backuppath)
                        force_rename(self._tmppath, self.filepath)
                    except EnvironmentError:
                        try_unlink(self._tmppath)
                        raise
            finally:
                self._tmppath = None
        #elif self._state == self.CLOSED: pass

    def rollback(self):
        if self._state == self.UNOPENED:
            raise ValueError('Cannot close unopened file')
        elif self._state == self.OPEN:
            self._state = self.CLOSED
            self._close()
            if self.move_first:
                force_rename(self._tmppath, self.filepath)
            else:
                try_unlink(self._tmppath)
            self._tmppath = None
        elif self._state == self.CLOSED:
            raise ValueError('Cannot rollback closed file')

    @property
    def closed(self):
        return self._state != self.OPEN

    def read(self, size=-1):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.read(size)

    def readline(self, size=-1):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.readline(size)

    def readlines(self, sizehint=-1):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.readlines(sizehint)

    def write(self, s):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        self.output.write(s)

    def writelines(self, seq):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        self.output.writelines(seq)

    def __iter__(self):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return iter(self.input)

    def flush(self):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        self.output.flush()


class InPlaceBytes(InPlaceABC):
    def _open_read(self, path):
        return open(path, 'rb')

    def _open_write(self, path):
        return open(path, 'wb')

    def readinto(self, b):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.readinto(b)

    def readall(self):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.readall()


class InPlace(InPlaceABC):
    def __init__(self, name, backup=None, backup_ext=None, delay_open=False,
                 move_first=False, encoding=None, errors=None, newline=None):
        self.encoding = encoding
        self.errors = errors
        self.newline = newline
        super(InPlace, self).__init__(
            name, backup, backup_ext, delay_open, move_first,
        )

    def _open_read(self, path):
        return io.open(path, 'rt', encoding=self.encoding, errors=self.errors,
                       newline=self.newline)

    def _open_write(self, path):
        return io.open(path, 'wt', encoding=self.encoding, errors=self.errors,
                       newline=self.newline)


def copystats(from_file, to_file):
    shutil.copystat(from_file, to_file)
    if hasattr(os, 'chown'):
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
