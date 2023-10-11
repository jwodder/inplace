from __future__ import annotations
from pathlib import Path
import pytest
from in_place import InPlace
from test_in_place_util import NLB, UNICODE, pylistdir


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


def test_bytes_useless_after_close(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, "b", backup_ext="~") as fp:
        assert not fp.closed
    assert fp.closed
    with pytest.raises(ValueError):
        fp.readinto(bytearray(42))
