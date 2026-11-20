"""Locate newest PX4 ULog on disk without pyulog."""

import os
from pathlib import Path


def newest_ulg_under(root: Path) -> Path | None:
    if not root.is_dir():
        return None
    logs = sorted(root.rglob("*.ulg"), key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def default_px4_log_root() -> Path:
    override = os.environ.get("PX4_ULOG_DIR", "")
    if override:
        return Path(override)
    px4 = os.environ.get("PX4_AUTOPILOT_DIR", "")
    if px4:
        candidate = Path(px4) / "build" / "px4_sitl_default" / "rootfs" / "log"
        if candidate.is_dir():
            return candidate
    return Path.home() / "PX4-Autopilot" / "build" / "px4_sitl_default" / "rootfs" / "log"