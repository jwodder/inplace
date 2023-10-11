from __future__ import annotations
from pathlib import Path
import pytest
from in_place import InPlace
from test_in_place_util import UNICODE, pylistdir


def test_py3_textstr(tmp_path: Path) -> None:
    """Assert that `InPlace` works with text strings in Python 3"""
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, encoding="utf-8") as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        print(UNICODE, file=fp)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text(encoding="utf-8") == UNICODE + "\n"


def test_py3_not_bytestr(tmp_path: Path) -> None:
    """Assert that `InPlace` does not work with byte strings in Python 3"""
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, encoding="utf-8") as fp:
        txt = fp.read()
        assert isinstance(txt, str)
        assert txt == UNICODE
        bs = txt.encode("utf-16")
        with pytest.raises(TypeError):
            # `print()` would stringify `bs` to `b'...'`, which is not what we
            # want.
            fp.write(bs)  # type: ignore[arg-type]
