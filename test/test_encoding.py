from   unicodedata        import normalize
import pytest
from   in_place           import InPlace
from   test_in_place_util import UNICODE, pylistdir

def test_utf8_nobackup(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p), 't', encoding='utf-8') as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        fp.write(normalize('NFD', txt))
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_text('utf-8') == u'a\u030Ae\u0301i\u0302\xF8u\u0308\n'

def test_utf8_as_latin1(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p), 't', encoding='latin-1') as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == u'\xc3\xa5\xc3\xa9\xc3\xae\xc3\xb8\xc3\xbc\n'
        fp.write(UNICODE)
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_binary() == b'\xE5\xE9\xEE\xF8\xFC\n'

def test_latin1_as_utf8(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'latin-1')
    with InPlace(str(p), 't', encoding='utf-8') as fp:
        with pytest.raises(UnicodeDecodeError):
            fp.read()

def test_latin1_as_utf8_replace(tmpdir):
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'latin-1')
    with InPlace(str(p), 't', encoding='utf-8', errors='replace') as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == u'\uFFFD\uFFFD\uFFFD\uFFFD\uFFFD\n'
        fp.write(txt)
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_text('utf-8') == u'\uFFFD\uFFFD\uFFFD\uFFFD\uFFFD\n'
