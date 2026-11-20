"""Tests for ULog metrics persistence."""

from pathlib import Path

from dao.flight_log.ulg_metrics_dao import UlgMetricsDao
from services.fake_ulg_parser import FakeUlgReader


def test_save_run_copies_and_parses(tmp_path: Path) -> None:
    source = tmp_path / "source.ulg"
    source.write_bytes(b"PX4ULog")
    dao = UlgMetricsDao(log_dir=tmp_path / "archive")
    reader = FakeUlgReader(flight_time_s=10.0, max_position_error_m=0.5)
    dest, metrics = dao.save_run(str(source), reader)
    assert dest.exists()
    assert metrics.flight_time_s == 10.0
    assert metrics.max_position_error_m == 0.5
    assert dest.with_suffix(".metrics.json").exists()