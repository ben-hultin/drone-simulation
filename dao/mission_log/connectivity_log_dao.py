"""Append-only JSON logs for SITL connectivity checks."""

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ConnectivityLogDao:
    """Writes connectivity mission results under a configurable directory."""

    def __init__(self, log_dir: Path | None = None) -> None:
        default = Path.home() / ".local" / "share" / "drone-simulation" / "mission_logs"
        self._log_dir = log_dir or default
        self._log_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self._log_dir, 0o700)

    def append(self, payload: dict[str, Any]) -> Path:
        """Persist one connectivity result and return the file path."""
        stamped = {**payload, "recorded_at": datetime.now(UTC).isoformat()}
        name = f"connectivity_{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%f')}.json"
        path = self._log_dir / name
        path.write_text(json.dumps(stamped, indent=2), encoding="utf-8")
        return path