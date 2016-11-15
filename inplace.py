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
                self._tmppath = self.backup
            else:
                fd, tmppath = tempfile.mkstemp(prefix='inplace')
                os.close(fd)
                self._tmppath = tmppath
            shutil.copyfile(self.filepath, self._tmppath)
            shutil.copystat(self.filepath, self._tmppath)
            st = os.stat(self.filepath)
            # Based on GNU sed's behavior:
            try:
                os.chown(self._tmppath, st.st_uid, st.st_gid)
            except EnvironmentError:
                try:
                    os.chown(self._tmppath, -1, st.st_gid)
                except EnvironmentError:
                    pass
            self._infile = self._open_read(self._tmppath)
            self._outfile = self._open_write(self.filepath)
        ###else: error?

    @abc.abstractmethod
    def _open_read(self, path):
        pass

    @abc.abstractmethod
    def _open_write(self, path):
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
                    os.unlink(self._tmppath)
                except EnvironmentError as e:
                    if e.errno != ENOENT:
                        raise
            self._tmppath = None
        ###else: error?

    def discard(self):
        if self._infile is not None:
            self._close()
            shutil.copyfile(self._tmppath, self.filepath)
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
