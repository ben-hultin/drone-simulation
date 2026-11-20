"""Persist ULog copies and parsed metrics."""

import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

from dao.flight_log.ulg_reader_protocol import UlgFlightMetrics, UlgReader


class UlgMetricsDao:
    """Copies ULog files and records parsed metrics as JSON sidecars."""

    def __init__(self, log_dir: Path | None = None, reader: UlgReader | None = None) -> None:
        default = Path.home() / ".local" / "share" / "drone-simulation" / "flight_logs"
        self._log_dir = log_dir or default
        self._log_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self._log_dir, 0o700)
        self._reader = reader

    def save_run(self, source_ulg: str, reader: UlgReader) -> tuple[Path, UlgFlightMetrics]:
        """Copy ULog into log dir and return metrics from reader."""
        source = Path(source_ulg)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
        dest = self._log_dir / f"run_{stamp}.ulg"
        shutil.copy2(source, dest)
        metrics = reader.parse(str(dest))
        sidecar = dest.with_suffix(".metrics.json")
        sidecar.write_text(
            _metrics_payload(metrics),
            encoding="utf-8",
        )
        return dest, metrics

    def parse_existing(self, ulg_path: str) -> UlgFlightMetrics:
        if self._reader is None:
            raise RuntimeError("ulg_reader_not_configured")
        return self._reader.parse(ulg_path)


def _metrics_payload(metrics: UlgFlightMetrics) -> str:
    import json

    return json.dumps(
        {
            "flight_time_s": metrics.flight_time_s,
            "max_position_error_m": metrics.max_position_error_m,
        },
        indent=2,
    )