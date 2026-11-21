"""Tests for rosbag metadata persistence."""

from pathlib import Path

from dao.mission_log.rosbag_log_dao import RosbagLogDao


def test_record_run_writes_sidecar(tmp_path: Path) -> None:
    dao = RosbagLogDao(log_dir=tmp_path)
    record = dao.record_run("hover_5m_depth")
    assert record.bag_path.is_file()
    sidecar = record.bag_path.with_suffix(".bag.json")
    assert sidecar.is_file()
    assert "vehicle_odometry" in sidecar.read_text(encoding="utf-8")