from   __future__         import print_function
import sys
import pytest
from   in_place           import InPlace
from   test_in_place_util import UNICODE, pylistdir

pytestmark = pytest.mark.skipif(sys.version_info[0] < 3, reason='Python 3 only')

def test_py3_textstr(tmpdir):
    """ Assert that `InPlace` works with text strings in Python 3 """
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p)) as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        print(UNICODE, file=fp)
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_text('utf-8') == UNICODE + '\n'

def test_py3_not_bytestr(tmpdir):
    """ Assert that `InPlace` does not work with byte strings in Python 3 """
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p)) as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        txt = txt.encode('utf-8')
        with pytest.raises(TypeError):
            # `print()` would stringify `txt` to `b'...'`, which is not what we
            # want.
            fp.rewrite(txt)
