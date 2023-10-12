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
        files = pylistdir(tmp_path)
        assert len(files) == 2
        assert files[0].startswith("._in_place-")
        assert files[1] == "file.txt"
        for line in fp:
            assert isinstance(line, str)
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmp_path) == ["file.txt"]  # type: ignore[unreachable]
    assert p.read_text() == TEXT.swapcase()


def test_backup_ext(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup_ext="~") as fp:
        assert not fp.closed
        files = pylistdir(tmp_path)
        assert len(files) == 2
        assert files[0].startswith("._in_place-")
        assert files[1] == "file.txt"
        for line in fp:
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmp_path) == ["file.txt", "file.txt~"]  # type: ignore[unreachable]
    assert p.with_suffix(".txt~").read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_backup(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    bkp = tmp_path / "backup.txt"
    with InPlace(p, backup=bkp) as fp:
        assert not fp.closed
        files = pylistdir(tmp_path)
        assert len(files) == 2
        assert files[0].startswith("._in_place-")
        assert files[1] == "file.txt"
        for line in fp:
            fp.write(line.swapcase())
        assert not fp.closed
    assert fp.closed
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]  # type: ignore[unreachable]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


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
    with InPlace(p, backup=bkp) as fp:
        for i, line in enumerate(fp):
            fp.write(line.swapcase())
            if i == 5:
                p.unlink()
        with pytest.raises(OSError):
            fp.close()
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
    assert pylistdir(tmp_path) == ["backup.txt", "file.txt"]
    assert bkp.read_text() == TEXT
    assert p.read_text() == TEXT.swapcase()


def test_late_close(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()
    fp.close()
    assert pylistdir(tmp_path) == ["file.txt"]
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
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_rollback_then_inner_close(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
        assert pylistdir(tmp_path) == ["file.txt"]
        assert p.read_text() == TEXT
        fp.close()
        assert pylistdir(tmp_path) == ["file.txt"]
        assert p.read_text() == TEXT
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT


def test_rollback_then_outer_close(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p) as fp:
        for line in fp:
            fp.write(line.swapcase())
        fp.rollback()
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT
    fp.close()
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


def test_prechdir_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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


def test_same_backup_path(tmp_path: Path) -> None:
    assert pylistdir(tmp_path) == []
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    with InPlace(p, backup=p) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()


@pytest.mark.skipif(
    platform.system() == "Windows", reason="Windows barely has file modes"
)
def test_copy_executable_perm(tmp_path: Path) -> None:
    p = tmp_path / "file.txt"
    p.write_text(TEXT)
    p.chmod(0o755)
    with InPlace(p) as fp:
        for line in fp:
            fp.write(line.swapcase())
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_text() == TEXT.swapcase()
    assert p.stat().st_mode & 0o777 == 0o755


def test_empty_newline(tmp_path: Path) -> None:
    BYTES = (
        b"'Twas brillig, and the slithy toves\n"
        b"\tDid gyre and gimble in the wabe;\r"
        b"All mimsy were the borogoves,\r\n"
        b"\tAnd the mome raths outgrabe.\n"
    )
    p = tmp_path / "file.txt"
    p.write_bytes(BYTES)
    with InPlace(p, newline="") as fp:
        lines = fp.readlines()
        assert lines == [
            "'Twas brillig, and the slithy toves\n",
            "\tDid gyre and gimble in the wabe;\r",
            "All mimsy were the borogoves,\r\n",
            "\tAnd the mome raths outgrabe.\n",
        ]
        fp.writelines(ln.swapcase() for ln in lines)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_bytes() == BYTES.swapcase()


def test_unix_newline(tmp_path: Path) -> None:
    BYTES = (
        b"'Twas brillig, and the slithy toves\n"
        b"\tDid gyre and gimble in the wabe;\r"
        b"All mimsy were the borogoves,\r\n"
        b"\tAnd the mome raths outgrabe.\n"
    )
    p = tmp_path / "file.txt"
    p.write_bytes(BYTES)
    with InPlace(p, newline="\n") as fp:
        lines = fp.readlines()
        assert lines == [
            "'Twas brillig, and the slithy toves\n",
            "\tDid gyre and gimble in the wabe;\rAll mimsy were the borogoves,\r\n",
            "\tAnd the mome raths outgrabe.\n",
        ]
        fp.writelines(ln.swapcase() for ln in lines)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_bytes() == BYTES.swapcase()


def test_dos_newline(tmp_path: Path) -> None:
    BYTES = (
        b"'Twas brillig, and the slithy toves\n"
        b"\tDid gyre and gimble in the wabe;\r"
        b"All mimsy were the borogoves,\r\n"
        b"\tAnd the mome raths outgrabe.\n"
    )
    p = tmp_path / "file.txt"
    p.write_bytes(BYTES)
    with InPlace(p, newline="\r\n") as fp:
        lines = fp.readlines()
        assert lines == [
            (
                "'Twas brillig, and the slithy toves\n"
                "\tDid gyre and gimble in the wabe;\r"
                "All mimsy were the borogoves,\r\n"
            ),
            "\tAnd the mome raths outgrabe.\n",
        ]
        fp.writelines(ln.swapcase() for ln in lines)
    assert pylistdir(tmp_path) == ["file.txt"]
    assert p.read_bytes() == (
        b"'tWAS BRILLIG, AND THE SLITHY TOVES\r\n"
        b"\tdID GYRE AND GIMBLE IN THE WABE;\r"
        b"aLL MIMSY WERE THE BOROGOVES,\r\r\n"
        b"\taND THE MOME RATHS OUTGRABE.\r\n"
    )
