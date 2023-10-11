from __future__ import annotations
import os.path
from pathlib import Path
import pytest
from in_place import InPlace
from test_in_place_util import NLB, TEXT, UNICODE, pylistdir


def test_print_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(p, backup=bkp) as fp:
        for line in fp:
            print(line.swapcase(), end="", file=fp)
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_read1_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, "b") as fp:
        bs = fp.read1(5)
        assert 1 <= len(bs) <= 5
        assert bs[0] == 0xC3


def test_readinto_bytearray_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, "b") as fp:
        ba = bytearray(5)
        assert fp.readinto(ba) == 5
        assert ba == bytearray(b"\xC3\xA5\xC3\xA9\xC3")
        fp.write(ba)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_bytes() == b"\xC3\xA5\xC3\xA9\xC3"


def test_readinto1_bytearray_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, "b") as fp:
        ba = bytearray(5)
        r = fp.readinto1(ba)
        assert 1 <= r <= 5
        assert len(ba) == r
        assert ba[0] == 0xC3


def test_readlines_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        assert fp.readlines() == TEXT.splitlines(True)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == ""


def test_writelines_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text("")
    bkp = tmp_path / "backup.txt"
    with InPlace(p, backup=bkp) as fp:
        fp.writelines(TEXT.splitlines(True))
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == ""
    assert p.read_text() == TEXT


def test_readline_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for line in iter(fp.readline, ""):
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


def test_misc(tmp_path: Path) -> None:
    p = tmp_path / "file.txt"
    p.touch()
    with InPlace(p) as fp:
        assert fp.name == os.path.realpath(p)
        assert fp.readable()
        assert fp.writable()
        assert not fp.seekable()
        assert not fp.isatty()
        with pytest.raises(OSError):
            fp.seek(0)
        with pytest.raises(OSError):
            fp.tell()
        with pytest.raises(OSError):
            fp.truncate()
        with pytest.raises(OSError):
            fp.fileno()


def test_binary_iteration(tmp_path: Path) -> None:
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, mode="b") as fp:
        assert next(fp) == b"'Twas brillig, and the slithy toves" + NLB
        assert next(fp) == b"\tDid gyre and gimble in the wabe;" + NLB
