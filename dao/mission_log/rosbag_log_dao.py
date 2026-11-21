"""Record rosbag metadata alongside PX4 ULog runs."""

import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class RosbagRunRecord:
    scenario_name: str
    bag_path: Path
    topic_names: tuple[str, ...]
    recorded_at: str


class RosbagLogDao:
    def __init__(self, log_dir: Path | None = None) -> None:
        default = Path.home() / ".local" / "share" / "drone-simulation" / "rosbags"
        self._log_dir = log_dir or default
        self._log_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self._log_dir, 0o700)

    def record_run(
        self,
        scenario_name: str,
        *,
        topics: tuple[str, ...] = (
            "/fmu/out/vehicle_odometry",
            "/depth_camera",
            "/points",
        ),
    ) -> RosbagRunRecord:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%f")
        dest = self._log_dir / f"{scenario_name}_{stamp}.bag"
        dest.write_bytes(b"")
        record = RosbagRunRecord(
            scenario_name=scenario_name,
            bag_path=dest,
            topic_names=topics,
            recorded_at=datetime.now(UTC).isoformat(),
        )
        sidecar = dest.with_suffix(".bag.json")
        sidecar.write_text(json.dumps(asdict(record), default=str), encoding="utf-8")
        return record