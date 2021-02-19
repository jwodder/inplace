from   operator           import attrgetter
import os
from   os.path            import relpath
import platform
import pytest
from   in_place           import InPlace
from   test_in_place_util import TEXT

pytestmark = pytest.mark.xfail(
    platform.system() == "Windows" and platform.python_implementation() == "PyPy",
    reason='Symlinks are not implemented on PyPy on Windows as of v7.3.3',
)

def test_symlink_nobackup(tmp_path):
    assert list(tmp_path.iterdir()) == []
    realdir = tmp_path / "real"
    realdir.mkdir()
    real = realdir / 'realfile.txt'
    real.write_text(TEXT)
    linkdir = tmp_path / "link"
    linkdir.mkdir()
    link = linkdir / 'linkfile.txt'
    target = relpath(real, linkdir)
    link.symlink_to(target)
    with InPlace(str(link)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert list(realdir.iterdir()) == [real]
    assert list(linkdir.iterdir()) == [link]
    assert link.is_symlink()
    assert os.readlink(str(link)) == target
    assert link.read_text() == TEXT.swapcase()
    assert real.read_text() == TEXT.swapcase()

def test_symlink_backup_ext(tmp_path):
    assert list(tmp_path.iterdir()) == []
    realdir = tmp_path / "real"
    realdir.mkdir()
    real = realdir / 'realfile.txt'
    real.write_text(TEXT)
    linkdir = tmp_path / "link"
    linkdir.mkdir()
    link = linkdir / 'linkfile.txt'
    target = relpath(real, linkdir)
    link.symlink_to(target)
    with InPlace(str(link), backup_ext='~') as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert list(realdir.iterdir()) == [real]
    assert sorted(linkdir.iterdir(), key=attrgetter("name")) == [
        link,
        link.with_suffix(".txt~"),
    ]
    assert link.is_symlink()
    assert os.readlink(str(link)) == target
    assert link.with_suffix('.txt~').read_text() == TEXT
    assert link.read_text() == TEXT.swapcase()
    assert real.read_text() == TEXT.swapcase()

def test_symlink_backup(tmp_path):
    assert list(tmp_path.iterdir()) == []
    realdir = tmp_path / "real"
    realdir.mkdir()
    real = realdir / 'realfile.txt'
    real.write_text(TEXT)
    linkdir = tmp_path / "link"
    linkdir.mkdir()
    link = linkdir / 'linkfile.txt'
    target = relpath(real, linkdir)
    link.symlink_to(target)
    bkp = tmp_path / "backup.txt"
    with InPlace(str(link), backup=str(bkp)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert sorted(tmp_path.iterdir(), key=attrgetter("name")) == [
        bkp,
        linkdir,
        realdir,
    ]
    assert list(realdir.iterdir()) == [real]
    assert list(linkdir.iterdir()) == [link]
    assert link.is_symlink()
    assert os.readlink(str(link)) == target
    assert bkp.read_text() == TEXT
    assert link.read_text() == TEXT.swapcase()
    assert real.read_text() == TEXT.swapcase()
