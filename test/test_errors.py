from __future__ import annotations
from pathlib import Path
import pytest
from in_place import InPlace
from test_in_place_util import TEXT, pylistdir


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
