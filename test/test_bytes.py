import pytest
from   in_place           import InPlace
from   test_in_place_util import UNICODE, pylistdir

def test_bytes_iconv_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p), 'b') as fp:
        txt = fp.read()
        assert isinstance(txt, bytes)
        assert txt == b'\xc3\xa5\xc3\xa9\xc3\xae\xc3\xb8\xc3\xbc\n'
        fp.write(txt.decode('utf-8').encode('latin-1'))
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_binary() == b'\xE5\xE9\xEE\xF8\xFC\n'

def test_bytes_useless_after_close(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p), 'b', backup_ext='~') as fp:
        assert not fp.closed
    assert fp.closed
    with pytest.raises(ValueError):
        fp.readall()
    with pytest.raises(ValueError):
        fp.readinto(bytearray(42))
