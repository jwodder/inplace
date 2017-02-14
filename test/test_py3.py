import sys
import pytest
import six
from   in_place           import InPlace
from   test_in_place_util import UNICODE, pylistdir

pytestmark = pytest.mark.skipif(sys.version_info[0] < 3, reason='Python 3 only')

def test_py3_textstr(tmpdir, monkeypatch):
    """ Assert that `InPlace` works with text strings in Python 3 """
    monkeypatch.setenv('LC_ALL', 'utf-8')
    assert pylistdir(tmpdir) == []
    p = tmpdir.join("file.txt")
    p.write_text(UNICODE, 'utf-8')
    with InPlace(str(p)) as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        six.print_(UNICODE, file=fp)
    assert pylistdir(tmpdir) == ['file.txt']
    assert p.read_text('utf-8') == UNICODE + '\n'
