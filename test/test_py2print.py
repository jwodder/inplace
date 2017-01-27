import sys
import pytest
from   in_place           import InPlaceBytes
from   test_in_place_util import TEXT, pylistdir

@pytest.mark.skipif(sys.version_info[0] > 2, reason='Python 2 only')
def test_py2print_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    # Use InPlaceBytes because we're writing Python 2 `str`s
    with InPlaceBytes(str(p), backup=str(bkp)) as fp:
        for line in fp:
            print >>fp, len(line),
        print >>fp
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == ' '.join(str(len(line)) for line in TEXT.splitlines(True)) + '\n'
