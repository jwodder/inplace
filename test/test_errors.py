from __future__ import annotations
from pathlib import Path
import platform
import pytest
from in_place import InPlace
from test_in_place_util import TEXT, UNICODE, pylistdir


def test_backup_ext_and_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with pytest.raises(ValueError):
        InPlace(p, backup=bkp, backup_ext="~")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_empty_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with pytest.raises(ValueError):
        InPlace(p, backup_ext="")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_empty_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with pytest.raises(ValueError):
        InPlace(p, backup="")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


@pytest.mark.parametrize("backup", [None, "backup.txt"])
def test_bad_mode(tmp_path: Path, backup: str | None) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    backup_path = tmp_path / backup if backup is not None else None
    with pytest.raises(ValueError, match="invalid mode"):
        InPlace(p, mode="q", backup=backup_path)  # type: ignore[call-overload]
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_early_close_and_write_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.close()
        with pytest.raises(ValueError):
            fp.write("And another thing...\n")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


def test_early_close_and_write_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(p, backup=bkp) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.close()
        with pytest.raises(ValueError):
            fp.write("And another thing...\n")
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_rollback_and_write_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
        with pytest.raises(ValueError):
            fp.write("And another thing...\n")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_rollback_and_write_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(p, backup=bkp) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
        with pytest.raises(ValueError):
            fp.write("And another thing...\n")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_rollback_too_late(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup_ext="~") as fp:
        for line in fp:
            fp.write(line.swapcase())
    with pytest.raises(ValueError):
        fp.rollback()
    assert pylistdir(tmp_path) == ["file.txt", "file.txt~"]
    assert p.with_suffix(".txt~").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_backup_dirpath(tmp_path: Path) -> None:
    """
    Assert that using a path to a directory as the backup path raises an error
    when closing
    """
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    not_a_file = tmp_path / "not-a-file"
    not_a_file.mkdir()
    assert pylistdir(not_a_file) == []
    fp = InPlace(p, backup=not_a_file)
    fp.write("This will be discarded.\n")
    with pytest.raises(OSError):
        fp.close()
    assert pylistdir(tmp_path) == ["file.txt", "not-a-file"]
    assert p.read_text() == TEXT
    assert pylistdir(not_a_file) == []


def test_backup_nosuchdir(tmp_path: Path) -> None:
    """
    Assert that using a path to a file in a nonexistent directory as the backup
    path raises an error when closing
    """
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    fp = InPlace(p, backup=tmp_path / "nonexistent" / "backup.txt")
    fp.write("This will be discarded.\n")
    with pytest.raises(OSError):
        fp.close()
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_nonexistent(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    with pytest.raises(FileNotFoundError):
        InPlace(p)
    assert pylistdir(tmp_path) == []


def test_nonexistent_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    with pytest.raises(FileNotFoundError):
        InPlace(p, backup_ext="~")
    assert pylistdir(tmp_path) == []


def test_nonexistent_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    with pytest.raises(FileNotFoundError):
        InPlace(p, backup=tmp_path / "backup.txt")
    assert pylistdir(tmp_path) == []


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Windows barely has file modes"
)
def test_unwritable_dir(tmp_path: Path) -> None:
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    tmp_path.chmod(0o555)
    with pytest.raises(OSError):
        InPlace(p)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Windows barely has file modes"
)
def test_unreadable_file(tmp_path: Path) -> None:
    p = tmp_path / "file.txt"
    p.touch()
    p.chmod(0o000)
    with pytest.raises(OSError):
        InPlace(p)
    assert pylistdir(tmp_path) == ["file.txt"]


def test_useless_after_close(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup_ext="~") as fp:
        pass
    with pytest.raises(ValueError):
        fp.flush()
    with pytest.raises(ValueError):
        next(fp)
    with pytest.raises(ValueError):
        fp.read()
    with pytest.raises(ValueError):
        fp.readline()
    with pytest.raises(ValueError):
        fp.readlines()
    with pytest.raises(ValueError):
        fp.write("")
    with pytest.raises(ValueError):
        fp.writelines([""])


def test_not_reusable(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        pass
    with fp:
        with pytest.raises(ValueError):
            fp.flush()
        with pytest.raises(ValueError):
            next(fp)
        with pytest.raises(ValueError):
            fp.read()
        with pytest.raises(ValueError):
            fp.readline()
        with pytest.raises(ValueError):
            fp.readlines()
        with pytest.raises(ValueError):
            fp.write("")
        with pytest.raises(ValueError):
            fp.writelines([""])


def test_bytes_useless_after_close(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(UNICODE, encoding="utf-8")
    with InPlace(p, "b", backup_ext="~") as fp:
        pass
    with pytest.raises(ValueError):  # type: ignore[unreachable]
        fp.read1()
    with pytest.raises(ValueError):
        fp.readinto(bytearray(42))
    with pytest.raises(ValueError):
        fp.readinto1(bytearray(42))
