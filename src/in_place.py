"""
In-place file processing

The ``in_place`` module provides an ``InPlace`` class for reading & writing a
file "in-place": data that you write ends up at the same filepath that you read
from, and ``in_place`` takes care of all the necessary mucking about with
temporary files for you.

Visit <https://github.com/jwodder/inplace> for more information.
"""

__version__      = '0.5.0.dev1'
__author__       = 'John Thorvald Wodder II'
__author_email__ = 'inplace@varonathe.org'
__license__      = 'MIT'
__url__          = 'https://github.com/jwodder/inplace'

import os
import os.path
import shutil
import tempfile
from   warnings import warn

__all__ = ['InPlace', 'InPlaceBytes', 'InPlaceText']

class InPlace:
    """
    A class for reading from & writing to a file "in-place" (with data that you
    write ending up at the same filepath that you read from) that takes care of
    all the necessary mucking about with temporary files.

    :param name: The path to the file to open & edit in-place (resolved
        relative to the current directory at the time of the instance's
        creation)
    :type name: path-like

    :param string mode: Whether to operate on the file in binary or text mode.
        If ``mode`` is ``'b'``, the file will be opened in binary mode, and
        data will be read & written as `bytes` objects.  If ``mode`` is ``'t'``
        or unset, the file will be opened in text mode, and data will be read &
        written as `str` objects.

    :param backup: The path at which to save the file's original contents once
        editing has finished (resolved relative to the current directory at the
        time of the instance's creation); if `None` (the default), no backup is
        saved
    :type backup: path-like

    :param backup_ext: A string to append to ``name`` to get the path at which
        to save the file's original contents.  Cannot be empty.  ``backup`` and
        ``backup_ext`` are mutually exclusive.
    :type backup_ext: path-like

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

    :param kwargs: Additional keyword arguments to pass to `open()`
    """

    UNOPENED = 0
    OPEN = 1
    CLOSED = 2

    def __init__(self, name, mode=None, backup=None, backup_ext=None,
                 delay_open=False, move_first=False, **kwargs):
        cwd = os.getcwd()
        #: The path to the file to edit in-place
        self.name = os.fsdecode(name)
        #: Whether to operate on the file in binary or text mode
        self.mode = mode
        #: The absolute path of the file to edit in-place
        self.filepath = os.path.join(cwd, self.name)
        #: ``filepath`` with symbolic links resolved.  This is set just before
        #: opening the file.
        self.realpath = None
        if backup is not None:
            if backup_ext is not None:
                raise ValueError('backup and backup_ext are mutually exclusive')
            #: The absolute path of the backup file (if any) that the original
            #: contents of ``realpath`` will be moved to after editing
            self.backuppath = os.path.join(cwd, os.fsdecode(backup))
        elif backup_ext is not None:
            if not backup_ext:
                raise ValueError('backup_ext cannot be empty')
            self.backuppath = self.filepath + os.fsdecode(backup_ext)
        else:
            self.backuppath = None
        #: Whether to move the input file before opening and create the output
        #: file in its place instead of moving the files after closing
        self.move_first = move_first
        #: Additional arguments to pass to `open`
        self.kwargs = kwargs
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
            self.realpath = os.path.realpath(self.filepath)
            try:
                self.input = self.open_read(self.realpath)
                if self.move_first:
                    if self.backuppath is not None:
                        self._tmppath = self._mktemp(self.backuppath)
                    else:
                        self._tmppath = self._mktemp(self.realpath)
                    os.replace(self.realpath, self._tmppath)
                    self.output = self.open_write(self.realpath)
                    copystats(self._tmppath, self.realpath)
                else:
                    self._tmppath = self._mktemp(self.realpath)
                    self.output = self.open_write(self._tmppath)
                    copystats(self.realpath, self._tmppath)
            except Exception:
                self.rollback()
                raise
        else:
            raise ValueError('open() called twice on same filehandle')

    def open_read(self, path):
        """
        Open the file at ``path`` for reading and return a file-like object.
        Use :attr:`mode` to determine whether to open in binary or text mode.
        """
        if not self.mode or self.mode == 't':
            return open(path, 'r', **self.kwargs)
        elif self.mode == 'b':
            return open(path, 'rb', **self.kwargs)
        else:
            raise ValueError(f'{self.mode!r}: invalid mode')

    def open_write(self, path):
        """
        Open the file at ``path`` for writing and return a file-like object.
        Use :attr:`mode` to determine whether to open in binary or text mode.
        """
        if not self.mode or self.mode == 't':
            return open(path, 'w', **self.kwargs)
        elif self.mode == 'b':
            return open(path, 'wb', **self.kwargs)
        else:
            raise ValueError(f'{self.mode!r}: invalid mode')

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
        If called after the filehandle has already been closed (with either
        this method or :meth:`rollback`), :meth:`close` does nothing.

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
                            os.replace(self._tmppath, self.backuppath)
                        except IOError:
                            os.replace(self._tmppath, self.realpath)
                            self._tmppath = None
                            raise
                else:
                    if self.backuppath is not None:
                        os.replace(self.realpath, self.backuppath)
                    os.replace(self._tmppath, self.realpath)
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
                    os.replace(self._tmppath, self.realpath)
                else:
                    try_unlink(self._tmppath)
                self._tmppath = None
        else:
            assert self._state == self.CLOSED
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

    def readinto(self, b):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.readinto(b)

    def readall(self):
        if self._state != self.OPEN:
            raise ValueError('Filehandle is not currently open')
        return self.input.readall()

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


class InPlaceBytes(InPlace):
    """ Deprecated.  Please use `InPlace` with ``mode='b'`` instead. """

    def __init__(self, name, **kwargs):
        warn(
            'InPlaceBytes is deprecated.'
            '  Please use `InPlace(name, mode="b")` instead.',
            DeprecationWarning,
        )
        super(InPlaceBytes, self).__init__(name, mode='b', **kwargs)


class InPlaceText(InPlace):
    """ Deprecated.  Please use `InPlace` with ``mode='t'`` instead. """

    def __init__(self, name, **kwargs):
        warn(
            'InPlaceText is deprecated.'
            '  Please use `InPlace(name, mode="t")` instead.',
            DeprecationWarning,
        )
        super(InPlaceText, self).__init__(name, mode='t', **kwargs)


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
        except IOError:
            try:
                os.chown(to_file, -1, st.st_gid)
            except IOError:
                pass

def try_unlink(path):
    """
    Try to delete the file at ``path``.  If the file doesn't exist, do nothing;
    any other errors are propagated to the caller.
    """
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
