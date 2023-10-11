from __future__ import annotations
from pathlib import Path
from unicodedata import normalize
import pytest
from in_place import InPlaceBytes, InPlaceText
from test_in_place_util import NLB, UNICODE, pylistdir


def test_deprecated_bytes_iconv_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with pytest.warns(DeprecationWarning, match="InPlaceBytes is deprecated"):
        fp = InPlaceBytes(p)
    with fp:
        txt = fp.read()
        assert isinstance(txt, bytes)
        assert txt == b"\xc3\xa5\xc3\xa9\xc3\xae\xc3\xb8\xc3\xbc" + NLB
        fp.write(txt.decode("utf-8").encode("latin-1"))
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_bytes() == b"\xE5\xE9\xEE\xF8\xFC" + NLB


def test_deprecated_utf8_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with pytest.warns(DeprecationWarning, match="InPlaceText is deprecated"):
        fp = InPlaceText(p, encoding="utf-8")
    with fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        fp.write(normalize("NFD", txt))
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text(encoding="utf-8") == "a\u030Ae\u0301i\u0302\xF8u\u0308\n"
