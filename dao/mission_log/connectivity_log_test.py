"""Tests for connectivity log DAO."""

import json
from pathlib import Path

from dao.mission_log.connectivity_log_dao import ConnectivityLogDao


def test_append_connectivity_result(tmp_path: Path) -> None:
    dao = ConnectivityLogDao(log_dir=tmp_path)
    dao.append({"status": "ready", "endpoint": "udpin://0.0.0.0:14540"})
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload["status"] == "ready"