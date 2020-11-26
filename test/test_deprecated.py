from   unicodedata        import normalize
import pytest
from   in_place           import InPlaceBytes, InPlaceText
from   test_in_place_util import UNICODE, pylistdir

def test_deprecated_bytes_iconv_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with pytest.warns(DeprecationWarning, match='InPlaceBytes is deprecated'):
        fp = InPlaceBytes(str(p))
    with fp:
        txt = fp.read()
        assert isinstance(txt, bytes)
        assert txt == b'\xc3\xa5\xc3\xa9\xc3\xae\xc3\xb8\xc3\xbc\n'
        fp.write(txt.decode('utf-8').encode('latin-1'))
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_binary() == b'\xE5\xE9\xEE\xF8\xFC\n'

def test_deprecated_utf8_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with pytest.warns(DeprecationWarning, match='InPlaceText is deprecated'):
        fp = InPlaceText(str(p), encoding='utf-8')
    with fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        fp.write(normalize('NFD', txt))
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_text('utf-8') == u'a\u030Ae\u0301i\u0302\xF8u\u0308\n'
