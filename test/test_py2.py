import sys
import pytest
from   in_place           import InPlace
from   test_in_place_util import TEXT, UNICODE, pylistdir

pytestmark = pytest.mark.skipif(sys.version_info[0] > 2, reason='Python 2 only')

def test_py2print_backup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write(TEXT)
    bkp = tmpdir.join('backup.txt')
    with InPlace(str(p), backup=str(bkp)) as fp:
        for line in fp:
            print >>fp, len(line),
        print >>fp
    assert pylistdir(tmpdir) == ['backup.txt', 'file.txt']
    assert bkp.read() == TEXT
    assert p.read() == ' '.join(str(len(line)) for line in TEXT.splitlines(True)) + '\n'

def test_py2_bytestr(tmpdir):
    """ Assert that `InPlace` works with byte strings in Python 2 """
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p)) as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == b'\xc3\xa5\xc3\xa9\xc3\xae\xc3\xb8\xc3\xbc\n'
        print >>fp, txt.decode('utf-8').encode('latin-1')
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_binary() == b'\xE5\xE9\xEE\xF8\xFC\n\n'

def test_py2_not_textstr(tmpdir):
    """
    Assert that `InPlace` does not work with non-ASCII text strings in Python 2
    """
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p)) as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == b'\xc3\xa5\xc3\xa9\xc3\xae\xc3\xb8\xc3\xbc\n'
        txt = txt.decode('utf-8')
        with pytest.raises(UnicodeError):
            print >>fp, txt
