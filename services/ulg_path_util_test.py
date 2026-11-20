"""Tests for ULog path discovery."""

from pathlib import Path

from services.ulg_path_util import newest_ulg_under


def test_newest_ulg_under(tmp_path: Path) -> None:
    old = tmp_path / "old.ulg"
    new = tmp_path / "subdir" / "new.ulg"
    new.parent.mkdir()
    old.write_bytes(b"a")
    new.write_bytes(b"b")
    picked = newest_ulg_under(tmp_path)
    assert picked == new or picked == old