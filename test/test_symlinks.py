import os
from os.path import relpath
from pathlib import Path
import platform
import sys
import pytest
from in_place import InPlace
from test_in_place_util import TEXT, pylistdir

pytestmark = pytest.mark.xfail(
    platform.system() == "Windows"
    and hasattr(sys, "pypy_version_info")
    and sys.pypy_version_info < (7, 3, 12),
    reason="Symlinks are not implemented on PyPy on Windows before v7.3.12",
)


def test_symlink_nobackup(tmp_path: Path) -> None:
    assert list(tmp_path.iterdir()) == []
    realdir = tmp_path / "real"
    realdir.mkdir()
    real = realdir / "realfile.txt"
    real.write_text(TEXT)
    linkdir = tmp_path / "link"
    linkdir.mkdir()
    link = linkdir / "linkfile.txt"
    target = relpath(real, linkdir)
    link.symlink_to(target)
    with InPlace(link) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert list(realdir.iterdir()) == [real]
    assert list(linkdir.iterdir()) == [link]
    assert link.is_symlink()
    assert os.readlink(link) == target
    assert link.read_text() == TEXT.swapcase()
    assert real.read_text() == TEXT.swapcase()


def test_symlink_backup_ext(tmp_path: Path) -> None:
    assert list(tmp_path.iterdir()) == []
    realdir = tmp_path / "real"
    realdir.mkdir()
    real = realdir / "realfile.txt"
    real.write_text(TEXT)
    linkdir = tmp_path / "link"
    linkdir.mkdir()
    link = linkdir / "linkfile.txt"
    target = relpath(real, linkdir)
    link.symlink_to(target)
    with InPlace(link, backup_ext="~") as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(realdir) == ["realfile.txt", "realfile.txt~"]
    assert not real.is_symlink()
    assert real.read_text() == TEXT.swapcase()
    assert not (realdir / "realfile.txt~").is_symlink()
    assert (realdir / "realfile.txt~").read_text() == TEXT
    assert pylistdir(linkdir) == ["linkfile.txt"]
    assert link.is_symlink()
    assert os.readlink(link) == target
    assert link.read_text() == TEXT.swapcase()


def test_symlink_backup(tmp_path: Path) -> None:
    assert list(tmp_path.iterdir()) == []
    realdir = tmp_path / "real"
    realdir.mkdir()
    real = realdir / "realfile.txt"
    real.write_text(TEXT)
    linkdir = tmp_path / "link"
    linkdir.mkdir()
    link = linkdir / "linkfile.txt"
    target = relpath(real, linkdir)
    link.symlink_to(target)
    bkp = tmp_path / "backup.txt"
    with InPlace(link, backup=bkp) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["backup.txt", "link", "real"]
    assert list(realdir.iterdir()) == [real]
    assert list(linkdir.iterdir()) == [link]
    assert link.is_symlink()
    assert os.readlink(link) == target
    assert bkp.read_text() == TEXT
    assert link.read_text() == TEXT.swapcase()
    assert real.read_text() == TEXT.swapcase()
