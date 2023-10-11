from __future__ import annotations
from pathlib import Path
from unicodedata import normalize
import pytest
from in_place import InPlace
from test_in_place_util import NLB, UNICODE, pylistdir


def test_utf8_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, "t", encoding="utf-8") as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        fp.write(normalize("NFD", txt))
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text(encoding="utf-8") == "a\u030Ae\u0301i\u0302\xF8u\u0308\n"


def test_utf8_as_latin1(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, "t", encoding="latin-1") as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == "\xc3\xa5\xc3\xa9\xc3\xae\xc3\xb8\xc3\xbc\n"
        fp.write(UNICODE)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_bytes() == b"\xE5\xE9\xEE\xF8\xFC" + NLB


def test_latin1_as_utf8(tmp_path: Path) -> None:
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="latin-1")
    with InPlace(p, "t", encoding="utf-8") as fp:
        with pytest.raises(UnicodeDecodeError):
            fp.read()


def test_latin1_as_utf8_replace(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="latin-1")
    with InPlace(p, "t", encoding="utf-8", errors="replace") as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == "\uFFFD\uFFFD\uFFFD\uFFFD\uFFFD\n"
        fp.write(txt)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text(encoding="utf-8") == "\uFFFD\uFFFD\uFFFD\uFFFD\uFFFD\n"


def test_bytes_iconv_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, "b") as fp:
        txt = fp.read()
        assert isinstance(txt, bytes)
        assert txt == b"\xc3\xa5\xc3\xa9\xc3\xae\xc3\xb8\xc3\xbc" + NLB
        fp.write(txt.decode("utf-8").encode("latin-1"))
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_bytes() == b"\xE5\xE9\xEE\xF8\xFC" + NLB
