"""
In-place file processing

The ``in_place`` module provides Python classes for reading & writing a file
"in-place": data that you write ends up at the same filepath that you read
from, and ``in_place`` takes care of all the necessary mucking about with
temporary files for you.

Visit <https://github.com/jwodder/inplace> for more information.
"""

__version__      = '0.2.0'
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

__all__ = ['InPlaceABC', 'InPlace', 'InPlaceBytes', 'InPlaceText']

@add_metaclass(abc.ABCMeta)
class InPlaceABC(object):
    """
    An abstract base class for reading from & writing to a file "in-place"
    (with data that you write ending up at the same filepath that you read
    from) that takes care of all the necessary mucking about with temporary
    files.  Concrete subclasses only need to implement `open_read` and
    `open_write` in order to define how & with what options the files are
    opened, and `InPlaceABC` takes care of the rest.

    Two concrete subclasses are provided with `InPlaceABC`: `InPlace`, for
    working with text files, and `InPlaceBytes`, for working with binary files.

    :param string name: The path to the file to open & edit in-place (resolved
        relative to the current directory at the time of the instance's
        creation)

    :param string backup: The path at which to save the file's original
        contents once editing has finished (resolved relative to the current
        directory at the time of the instance's creation); if `None` (the
        default), no backup is saved

    :param string backup_ext: A string to append to ``name`` to get the path at
        which to save the file's original contents.  Cannot be empty.
        ``backup`` and ``backup_ext`` are mutually exclusive.

    :param bool delay_open: If `True`, the newly-constructed instance will not
        be open, and the user must either explicitly call the :meth:`open()`
        method or use the instance as a context manager in order to open it.
        If `False` (the default), the instance will be automatically opened as
        soon as it is constructed.

    :param bool move_first: If `True`, the original (input) file will be moved
        to a temporary location before opening, and the output file will be
        created in its place.  If `False` (the default), the output file will
        be created at a temporary location, and neither file will be moved or
        deleted until :meth:`close()` is called.
    """

    UNOPENED = 0
    OPEN = 1
    CLOSED = 2

    def __init__(self, name, backup=None, backup_ext=None, delay_open=False,
                 move_first=False):
        cwd = os.getcwd()
        #: The path to the file to edit in-place
        self.name = name
        #: The absolute path of the file to edit in-place
        self.filepath = os.path.join(cwd, name)
        if backup is not None:
            if backup_ext is not None:
                raise ValueError('backup and backup_ext are mutually exclusive')
            #: The absolute path of the backup file (if any) that the original
            #: contents of ``filepath`` will be moved to after editing
            self.backuppath = os.path.join(cwd, backup)
        elif backup_ext is not None:
            if backup_ext == '':
                raise ValueError('backup_ext cannot be empty')
            self.backuppath = self.filepath + backup_ext
        else:
            self.backuppath = None
        #: Whether to move the input file before opening and create the output
        #: file in its place instead of moving the files after closing
        self.move_first = move_first
        #: The input filehandle from which data is read; only non-`None` while
        #: the instance is open
        self.input = None
        #: The output filehandle to which data is written; only non-`None`
        #: while the instance is open
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

    def _mktemp(self, filepath):
        """
        Create an empty temporary file in the same directory as ``filepath``
        and return the path to the new file
        """
        fd, tmppath = tempfile.mkstemp(
            dir=os.path.dirname(filepath),
            prefix='._in_place-',
        )
        os.close(fd)
        return tmppath

    def open(self):
        """
        Open the file :attr:`name` for reading and open a temporary file for
        writing.  If :attr:`move_first` is `True`, :attr:`name` will be moved
        to a temporary location before opening.

        If ``delay_open=True`` was passed to the instance's constructor, this
        method must be called (either explicitly or else implicitly by using
        the instance as a context manager) before the instance can be used for
        reading or writing.  If ``delay_open`` was `False` (the default), this
        method is called automatically by the constructor, and the user should
        not call it again.

        :raises ValueError: if called more than once on the same instance
        """
        if self._state < self.OPEN:
            self._state = self.OPEN
            try:
                self.input = self.open_read(self.filepath)
                if self.move_first:
                    if self.backuppath is not None:
                        self._tmppath = self._mktemp(self.backuppath)
                    else:
                        self._tmppath = self._mktemp(self.filepath)
                    force_rename(self.filepath, self._tmppath)
                    self.output = self.open_write(self.filepath)
                    copystats(self._tmppath, self.filepath)
                else:
                    self._tmppath = self._mktemp(self.filepath)
                    self.output = self.open_write(self._tmppath)
                    copystats(self.filepath, self._tmppath)
            except Exception:
                self.rollback()
                raise
        else:
            raise ValueError('open() called twice on same filehandle')

    @abc.abstractmethod
    def open_read(self, path):
        """
        Open the file at ``path`` for reading and return a file-like object.
        Concrete subclasses must override this method in order to customize how
        (and as what class) the file is opened.
        """
        pass

    @abc.abstractmethod
    def open_write(self, path):
        """
        Open the file at ``path`` for writing and return a file-like object.
        Concrete subclasses must override this method in order to customize how
        (and as what class) the file is opened.
        """
        pass

    def _close(self):
        """
        Close filehandles (if they aren't closed already) and set them to
        `None`
        """
        if self.input is not None:
            self.input.close()
            self.input = None
        if self.output is not None:
            self.output.close()
            self.output = None

    def close(self):
        """
        Close filehandles and move affected files to their final destinations.
        If called after the filhandle has already been closed (with either this
        method or :meth:`rollback`), :meth:`close` does nothing.

        :return: `None`
        :raises ValueError: if called before opening the filehandle
        """
        if self._state == self.UNOPENED:
            raise ValueError('Cannot close unopened file')
        elif self._state == self.OPEN:
            self._state = self.CLOSED
            self._close()
            try:
                if self.move_first:
                    if self.backuppath is not None:
                        try:
                            force_rename(self._tmppath, self.backuppath)
                        except EnvironmentError:
                            force_rename(self._tmppath, self.filepath)
                            self._tmppath = None
                            raise
                else:
                    if self.backuppath is not None:
                        force_rename(self.filepath, self.backuppath)
                    force_rename(self._tmppath, self.filepath)
            finally:
                if self._tmppath is not None:
                    try_unlink(self._tmppath)
                    self._tmppath = None
        #elif self._state == self.CLOSED: pass

    def rollback(self):
        """
        Close filehandles and remove/rename temporary files so that things look
        like they did before the `InPlace` instance was opened

        :return: `None`
        :raises ValueError: if called while the `InPlace` instance is not open
        """
        if self._state == self.UNOPENED:
            raise ValueError('Cannot close unopened file')
        elif self._state == self.OPEN:
            self._state = self.CLOSED
            self._close()
            if self._tmppath is not None:  # In case of error while opening
                if self.move_first:
                    force_rename(self._tmppath, self.filepath)
                else:
                    try_unlink(self._tmppath)
                self._tmppath = None
        elif self._state == self.CLOSED:
            raise ValueError('Cannot rollback closed file')

    @property
    def closed(self):
        """
        `True` iff the filehandle is not currently open.  Note that, if the
        filehandle was initialized with ``delay_open=True``, `closed` will be
        `True` until :meth:`open()` is called.
        """
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


class InPlace(InPlaceABC):
    """
    A file edited in-place; data is read & written as `str` objects, whatever
    those happen to be in your version of Python.
    """

    def open_read(self, path):
        return open(path, 'r')

    def open_write(self, path):
        return open(path, 'w')


class InPlaceBytes(InPlaceABC):
    """
    A binary file edited in-place; data is read & written as `str` (Python 2)
    or `bytes` (Python 3) objects.
    """

    def open_read(self, path):
        return open(path, 'rb')

    def open_write(self, path):
        return open(path, 'wb')

    def readinto(self, b):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.readinto(b)

    def readall(self):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.readall()


class InPlaceText(InPlaceABC):
    """
    A text (Unicode) file edited in-place; data is read & written as `unicode`
    (Python 2) or `str` (Python 3) objects.

    In addition to the parameters accepted by `InPlaceABC`, this class's
    constructor accepts optional ``encoding``, ``errors``, and ``newline``
    arguments that are applied to both reading and writing with the same
    meaning as the parameters to `io.open`.
    """

    def __init__(self, name, backup=None, backup_ext=None, delay_open=False,
                 move_first=False, encoding=None, errors=None, newline=None):
        self.encoding = encoding
        self.errors = errors
        self.newline = newline
        super(InPlaceText, self).__init__(
            name, backup, backup_ext, delay_open, move_first,
        )

    def open_read(self, path):
        return io.open(path, 'rt', encoding=self.encoding, errors=self.errors,
                       newline=self.newline)

    def open_write(self, path):
        return io.open(path, 'wt', encoding=self.encoding, errors=self.errors,
                       newline=self.newline)


def copystats(from_file, to_file):
    """
    Copy stat info from ``from_file`` to ``to_file`` using `shutil.copystat`.
    If possible, also copy the user and/or group ownership information.
    """
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
    """
    Move the file at ``oldpath`` to ``newpath``, deleting ``newpath``
    beforehand if necessary
    """
    if hasattr(os, 'replace'):  # Python 3.3+
        os.replace(oldpath, newpath)
    else:
        if sys.platform.startswith('win'):
            try_unlink(newpath)
        os.rename(oldpath, newpath)

def try_unlink(path):
    """
    Try to delete the file at ``path``.  If the file doesn't exist, do nothing;
    any other errors are propagated to the caller.
    """
    try:
        os.unlink(path)
    except EnvironmentError as e:
        if e.errno != ENOENT:
            raise
