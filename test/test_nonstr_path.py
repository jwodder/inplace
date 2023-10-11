from __future__ import annotations
from os import fsencode
from pathlib import Path
from typing import AnyStr, Generic
from in_place import InPlace
from test_in_place_util import TEXT, pylistdir


class PathLike(Generic[AnyStr]):
    def __init__(self, path: AnyStr) -> None:
        self.path: AnyStr = path

    def __fspath__(self) -> AnyStr:
        return self.path


def test_pathlike(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(PathLike(str(p))) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


def test_pathlike_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(PathLike(str(p)), backup_ext="~") as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt", "file.txt~"]
    assert p.with_suffix(".txt~").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_pathlike_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(PathLike(str(p)), backup=PathLike(str(bkp))) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_pathlike_bytes(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(PathLike(fsencode(p))) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


def test_pathlike_bytes_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(PathLike(fsencode(p)), backup_ext="~") as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt", "file.txt~"]
    assert p.with_suffix(".txt~").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_pathlike_bytes_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(PathLike(fsencode(p)), backup=PathLike(fsencode(bkp))) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_bytes(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(fsencode(p)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


def test_bytes_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(fsencode(p), backup_ext=fsencode("~")) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt", "file.txt~"]
    assert p.with_suffix(".txt~").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_bytes_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(fsencode(p), backup=fsencode(bkp)) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()
