from __future__ import annotations
import os
from pathlib import Path
import platform
import pytest
from in_place import InPlace
from test_in_place_util import TEXT, pylistdir


def test_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        assert not fp.closed
        for line in fp:
            assert isinstance(line, str)
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


def test_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup_ext="~") as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt", "file.txt~"]
    assert p.with_suffix(".txt~").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(p, backup=bkp) as fp:
        assert not fp.closed
        for line in fp:
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


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


def test_error_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with pytest.raises(RuntimeError):
        with InPlace(p, backup_ext="~") as fp:
            for i, line in enumerate(fp):
                fp.write(line.swapcase())
                if i > 5:
                    raise RuntimeError("I changed my mind.")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_pass_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p):
        pass
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == ""


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Cannot delete open file on Windows",
)
def test_delete_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for i, line in enumerate(fp):
            fp.write(line.swapcase())
            if i == 5:
                p.unlink()
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


@pytest.mark.skipif(
    platform.system() == "Windows",
    reason="Cannot delete open file on Windows",
)
def test_delete_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with pytest.raises(OSError):
        with InPlace(p, backup=bkp) as fp:
            for i, line in enumerate(fp):
                fp.write(line.swapcase())
                if i == 5:
                    p.unlink()
    assert pylistdir(tmp_path) == []


def test_early_close_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.close()
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


def test_early_close_and_write_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with pytest.raises(ValueError):
        with InPlace(p) as fp:
            for line in fp:
                fp.write(line.swapcase())
            fp.close()
            fp.write("And another thing...\n")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


def test_early_close_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(p, backup=bkp) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.close()
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_early_close_and_write_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with pytest.raises(ValueError):
        with InPlace(p, backup=bkp) as fp:
            for line in fp:
                fp.write(line.swapcase())
            fp.close()
            fp.write("And another thing...\n")
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_rollback_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_rollback_and_write_nobackup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with pytest.raises(ValueError):
        with InPlace(p) as fp:
            for line in fp:
                fp.write(line.swapcase())
            fp.rollback()
            fp.write("And another thing...\n")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_rollback_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(p, backup=bkp) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_rollback_and_write_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with pytest.raises(ValueError):
        with InPlace(p, backup=bkp) as fp:
            for line in fp:
                fp.write(line.swapcase())
            fp.rollback()
            fp.write("And another thing...\n")
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_overwrite_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    bkp.write_text("This is not the file you are looking for.\n")
    with InPlace(p, backup=bkp) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_rollback_overwrite_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    bkp.write_text("This is not the file you are looking for.\n")
    with InPlace(p, backup=bkp) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == "This is not the file you are looking for.\n"
    assert p.read_text() == TEXT


def test_prechdir_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPach) -> None:
    assert pylistdir(tmp_path) == []
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup="backup.txt") as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert (tmp_path / "backup.txt").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_postchdir_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Assert that changing directory after opening an InPlace object works"""
    filedir = tmp_path / "filedir"
    filedir.mkdir()
    wrongdir = tmp_path / "wrongdir"
    wrongdir.mkdir()
    p = filedir / "file.txt"
    p.write_text(TEXT)
    monkeypatch.chdir(filedir)
    with InPlace("file.txt", backup="backup.txt") as fp:
        monkeypatch.chdir(wrongdir)
        for line in fp:
            fp.write(line.swapcase())
    assert os.getcwd() == str(wrongdir)
    assert pylistdir(wrongdir) == []
    assert pylistdir(filedir) == ["backup.txt", "file.txt"]
    assert (filedir / "backup.txt").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_different_dir_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    filedir = tmp_path / "filedir"
    filedir.mkdir()
    bkpdir = tmp_path / "bkpdir"
    bkpdir.mkdir()
    p = filedir / "file.txt"
    p.write_text(TEXT)
    with InPlace(
        os.path.join("filedir", "file.txt"), backup=os.path.join("bkpdir", "backup.txt")
    ) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(filedir) == ["file.txt"]
    assert pylistdir(bkpdir) == ["backup.txt"]
    assert (bkpdir / "backup.txt").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_different_dir_file_backup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Assert that if the input filepath contains a directory component and the
    backup path does not, the backup file will be created in the current
    directory
    """
    monkeypatch.chdir(tmp_path)
    filedir = tmp_path / "filedir"
    filedir.mkdir()
    p = filedir / "file.txt"
    p.write_text(TEXT)
    with InPlace(
        os.path.join("filedir", "file.txt"),
        backup="backup.txt",
    ) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["backup.txt", "filedir"]
    assert pylistdir(filedir) == ["file.txt"]
    assert (tmp_path / "backup.txt").read_text() == TEXT
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


def test_with_nonexistent(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    with pytest.raises(FileNotFoundError):
        with InPlace(p):
            raise AssertionError("Not reached")
    assert pylistdir(tmp_path) == []


def test_nonexistent_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    with pytest.raises(FileNotFoundError):
        InPlace(p, backup_ext="~")
    assert pylistdir(tmp_path) == []


def test_with_nonexistent_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    with pytest.raises(FileNotFoundError):
        with InPlace(p, backup_ext="~"):
            raise AssertionError("Not reached")
    assert pylistdir(tmp_path) == []


def test_reentrant_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup_ext="~") as fp:
        with fp:
            for line in fp:
                fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt", "file.txt~"]
    assert p.with_suffix(".txt~").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_use_and_reenter_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup_ext="~") as fp:
        fp.write(fp.readline().swapcase())
        with fp:
            for line in fp:
                fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt", "file.txt~"]
    assert p.with_suffix(".txt~").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_var_changes(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup_ext="~") as fp:
        assert not fp.closed
        assert fp.input is not None
        assert fp.output is not None
        assert fp._tmppath is not None
    assert fp.closed
    assert fp.input is None
    assert fp.output is None
    assert fp._tmppath is None


def test_useless_after_close(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup_ext="~") as fp:
        assert not fp.closed
    assert fp.closed
    with pytest.raises(ValueError):
        fp.flush()
    with pytest.raises(ValueError):
        iter(fp)
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
