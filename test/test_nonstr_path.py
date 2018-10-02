import sys
import pytest
from   in_place           import InPlace
from   test_in_place_util import TEXT, pylistdir

class PathLike(object):
    def __init__(self, path):
        self.path = path

    def __fspath__(self):
        return self.path


@pytest.mark.skipif(sys.version_info[:2] < (3,6), reason='Python 3.6+ only')
def test_pathlike(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(PathLike(str(p))) as fp:
        assert not fp.closed
        for line in fp:
            assert isinstance(line, str)
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

@pytest.mark.skipif(sys.version_info[:2] < (3,6), reason='Python 3.6+ only')
def test_pathlike_backup_ext(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(PathLike(str(p)), backup_ext='~') as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()

@pytest.mark.skipif(sys.version_info[:2] < (3,6), reason='Python 3.6+ only')
def test_pathlike_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(PathLike(str(p)), backup=PathLike(str(bkp))) as fp:
        assert not fp.closed
        for line in fp:
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

@pytest.mark.skipif(sys.version_info[:2] < (3,6), reason='Python 3.6+ only')
def test_pathlike_bytes(tmpdir):
    from os import fsencode
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(PathLike(fsencode(str(p)))) as fp:
        assert not fp.closed
        for line in fp:
            assert isinstance(line, str)
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

@pytest.mark.skipif(sys.version_info[:2] < (3,6), reason='Python 3.6+ only')
def test_pathlike_bytes_backup_ext(tmpdir):
    from os import fsencode
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(PathLike(fsencode(str(p))), backup_ext='~') as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()

@pytest.mark.skipif(sys.version_info[:2] < (3,6), reason='Python 3.6+ only')
def test_pathlike_bytes_backup(tmpdir):
    from os import fsencode
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(
        PathLike(fsencode(str(p))),
        backup=PathLike(fsencode(str(bkp))),
    ) as fp:
        assert not fp.closed
        for line in fp:
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()

@pytest.mark.skipif(sys.version_info[0] < 3, reason='Python 3 only')
def test_bytes(tmpdir):
    from os import fsencode
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(fsencode(str(p))) as fp:
        assert not fp.closed
        for line in fp:
            assert isinstance(line, str)
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read() == TEXT.swapcase()

@pytest.mark.skipif(sys.version_info[0] < 3, reason='Python 3 only')
def test_bytes_backup_ext(tmpdir):
    from os import fsencode
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    with InPlace(fsencode(str(p)), backup_ext=fsencode('~')) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmpdir) == ['file.txt', 'file.txt~']
    assert p.new(ext='txt~').read() == TEXT
    assert p.read() == TEXT.swapcase()

@pytest.mark.skipif(sys.version_info[0] < 3, reason='Python 3 only')
def test_bytes_backup(tmpdir):
    from os import fsencode
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(fsencode(str(p)), backup=fsencode(str(bkp))) as fp:
        assert not fp.closed
        for line in fp:
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == TEXT.swapcase()
