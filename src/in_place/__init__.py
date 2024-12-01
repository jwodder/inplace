"""
In-place file processing

The ``in_place`` module provides an ``InPlace`` class for reading & writing a
file "in-place": data that you write ends up at the same filepath that you read
from, and ``in_place`` takes care of all the necessary mucking about with
temporary files for you.

Visit <https://github.com/jwodder/inplace> for more information.
"""

from __future__ import annotations
from collections.abc import Iterable
import os
import os.path
import shutil
import tempfile
from types import TracebackType
from typing import IO, TYPE_CHECKING, Any, AnyStr, Literal, Union, overload

if TYPE_CHECKING:
    from typing_extensions import Buffer

__version__ = "1.0.1"
__author__ = "John Thorvald Wodder II"
__author_email__ = "inplace@varonathe.org"
__license__ = "MIT"
__url__ = "https://github.com/jwodder/inplace"

__all__ = ["InPlace"]

AnyPath = Union[str, bytes, "os.PathLike[str]", "os.PathLike[bytes]"]


class InPlace(IO[AnyStr]):
    """
    A class for reading from & writing to a file "in-place" (with data that you
    write ending up at the same filepath that you read from) that takes care of
    all the necessary mucking about with temporary files.

    :param name: The path to the file to open & edit in-place (resolved
        relative to the current directory at the time of the instance's
        creation)
    :type name: path-like

    :param string mode: Whether to operate on the file in binary or text mode.
        If ``mode`` is ``"b"``, the file will be opened in binary mode, and
        data will be read & written as `bytes` objects.  If ``mode`` is ``"t"``
        or unset, the file will be opened in text mode, and data will be read &
        written as `str` objects.

    :param backup: The path at which to save the file's original contents once
        editing has finished (resolved relative to the current directory at the
        time of the instance's creation); if `None` (the default), no backup is
        saved.  Cannot be empty.
    :type backup: path-like

    :param backup_ext: A string to append to ``name`` to get the path at which
        to save the file's original contents.  Cannot be empty.  ``backup`` and
        ``backup_ext`` are mutually exclusive.
    :type backup_ext: path-like

    :param kwargs: Additional keyword arguments to pass to `open()`
    """

    @overload
    def __init__(
        self: InPlace[str],
        name: AnyPath,
        mode: Literal["t", None] = None,
        backup: AnyPath | None = None,
        backup_ext: AnyPath | None = None,
        **kwargs: Any,
    ) -> None: ...

    @overload
    def __init__(
        self: InPlace[bytes],
        name: AnyPath,
        mode: Literal["b"],
        backup: AnyPath | None = None,
        backup_ext: AnyPath | None = None,
        **kwargs: Any,
    ) -> None: ...

    def __init__(
        self,
        name: AnyPath,
        mode: Literal["t", "b", None] = None,
        backup: AnyPath | None = None,
        backup_ext: AnyPath | None = None,
        **kwargs: Any,
    ) -> None:
        cwd = os.getcwd()
        #: The path to the file to edit in-place
        self._name = os.fsdecode(name)
        #: The absolute path of the file to edit in-place, with symbolic links
        #: resolved
        self._path = os.path.realpath(os.path.join(cwd, self._name))
        #: The absolute path of the backup file (if any) that the original
        #: contents of ``path`` will be moved to after editing
        self._backuppath: str | None
        if backup is not None:
            if backup_ext is not None:
                raise ValueError("backup and backup_ext are mutually exclusive")
            b = os.fsdecode(backup)
            if not b:
                raise ValueError("backup cannot be empty")
            self._backuppath = os.path.join(cwd, b)
        elif backup_ext is not None:
            be = os.fsdecode(backup_ext)
            if not be:
                raise ValueError("backup_ext cannot be empty")
            self._backuppath = self._path + be
        else:
            self._backuppath = None
        if mode not in (None, "t", "b"):
            raise ValueError(f"{mode!r}: invalid mode")
        #: `True` iff the filehandle is closed
        self._closed = False
        #: The absolute path to the temporary file
        self._tmppath = self._mktemp(self._path)
        try:
            #: The output filehandle to which data is written
            self.output: IO[AnyStr]
            if mode is None or mode == "t":
                self.output = open(self._tmppath, "w", **kwargs)
            else:
                self.output = open(self._tmppath, "wb", **kwargs)
        except Exception:
            try_unlink(self._tmppath)
            raise
        try:
            copystats(self._path, self._tmppath)
        except Exception:
            self.output.close()
            try_unlink(self._tmppath)
            raise
        try:
            #: The input filehandle from which data is read
            self.input: IO[AnyStr]
            if mode is None or mode == "t":
                self.input = open(self._path, "r", **kwargs)
            else:
                self.input = open(self._path, "rb", **kwargs)
        except Exception:
            self.output.close()
            try_unlink(self._tmppath)
            raise

    def __enter__(self) -> InPlace[AnyStr]:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: TracebackType | None,
    ) -> None:
        if not self.closed:
            if exc_type is not None:
                self.rollback()
            else:
                self.close()

    def _mktemp(self, filepath: str) -> str:
        """
        Create an empty temporary file in the same directory as ``filepath``
        and return the path to the new file
        """
        fd, tmppath = tempfile.mkstemp(
            dir=os.path.dirname(filepath),
            prefix="._in_place-",
        )
        os.close(fd)
        return tmppath

    def _close(self) -> None:
        """Close filehandles and set them to `None`"""
        self._closed = True
        self.input.close()
        self.output.close()

    def close(self) -> None:
        """
        Close filehandles and move affected files to their final destinations.
        If called after the filehandle has already been closed (with either
        this method or :meth:`rollback`), :meth:`close` does nothing.

        :return: `None`
        """
        if not self.closed:
            self._close()
            try:
                if self._backuppath is not None:
                    os.replace(self._path, self._backuppath)
                os.replace(self._tmppath, self._path)
            finally:
                try_unlink(self._tmppath)

    def rollback(self) -> None:
        """
        Close filehandles and remove/rename temporary files so that things look
        like they did before the `InPlace` instance was opened

        :return: `None`
        :raises ValueError: if called after the `InPlace` instance is closed
        """
        if not self.closed:
            self._close()
            try_unlink(self._tmppath)
        else:
            raise ValueError("Cannot rollback closed file")

    @property
    def name(self) -> str:
        return self._name

    @property
    def closed(self) -> bool:
        return self._closed

    def read(self, size: int = -1) -> AnyStr:
        return self.input.read(size)

    def read1(self: InPlace[bytes], size: int = -1) -> bytes:
        bs = self.input.read1(size)  # type: ignore[attr-defined]
        assert isinstance(bs, bytes)
        return bs

    def readline(self, size: int = -1) -> AnyStr:
        return self.input.readline(size)

    def readlines(self, sizehint: int = -1) -> list[AnyStr]:
        return self.input.readlines(sizehint)

    def readinto(self: InPlace[bytes], b: Buffer) -> int:
        r = self.input.readinto(b)  # type: ignore[attr-defined]
        assert isinstance(r, int)
        return r

    def readinto1(self: InPlace[bytes], b: Buffer) -> int:
        r = self.input.readinto1(b)  # type: ignore[attr-defined]
        assert isinstance(r, int)
        return r

    def write(self, s: AnyStr) -> int:
        return self.output.write(s)

    def writelines(self, seq: Iterable[AnyStr]) -> None:
        self.output.writelines(seq)

    def __iter__(self) -> InPlace[AnyStr]:
        return self

    def __next__(self) -> AnyStr:
        return next(self.input)

    def flush(self) -> None:
        self.output.flush()

    def readable(self) -> bool:
        return True

    def writable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return False

    def seek(self, _offset: int, _whence: int = 0) -> int:
        raise OSError(f"{type(self).__name__} does not support seek()")

    def tell(self) -> int:
        raise OSError(f"{type(self).__name__} does not support tell()")

    def truncate(self, _size: int | None = None) -> int:
        raise OSError(f"{type(self).__name__} does not support truncate()")

    def fileno(self) -> int:
        raise OSError(f"{type(self).__name__} does not support fileno()")

    def isatty(self) -> bool:
        return False


def copystats(from_file: str, to_file: str) -> None:
    """
    Copy stat info from ``from_file`` to ``to_file`` using `shutil.copystat`.
    If possible, also copy the user and/or group ownership information.
    """
    shutil.copystat(from_file, to_file)
    if hasattr(os, "chown"):
        st = os.stat(from_file)
        # Based on GNU sed's behavior:
        try:
            os.chown(to_file, st.st_uid, st.st_gid)
        except IOError:
            try:
                os.chown(to_file, -1, st.st_gid)
            except IOError:
                pass


def try_unlink(path: str) -> None:
    """
    Try to delete the file at ``path``.  If the file doesn't exist, do nothing;
    any other errors are propagated to the caller.
    """
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
