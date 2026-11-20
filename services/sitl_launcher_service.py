"""Start and stop PX4 SITL + Gazebo when toolchain is present."""

import os
import signal
import subprocess  # nosec B404 — fixed-arg launcher, no shell
from dataclasses import dataclass
from pathlib import Path

from services.toolchain_service import probe_toolchain


@dataclass(frozen=True)
class SitlLauncherConfig:
    px4_autopilot_dir: Path
    target: str = "gz_x500"
    headless: bool = True


_ALLOWED_SITL_TARGETS = frozenset({"gz_x500", "gz_x500_depth"})


class SitlLauncherService:
    """Manages a child `make px4_sitl` process; never starts without PX4_AUTOPILOT_DIR."""

    def __init__(self, config: SitlLauncherConfig | None = None) -> None:
        self._config = config or _config_from_env()
        self._process: subprocess.Popen[str] | None = None

    @property
    def can_launch(self) -> bool:
        report = probe_toolchain()
        return (
            report.px4_on_path or self._config.px4_autopilot_dir.is_dir()
        ) and report.gazebo_on_path

    def start(self) -> bool:
        if not self.can_launch:
            return False
        if self._config.target not in _ALLOWED_SITL_TARGETS:
            return False
        if self._process is not None:
            return True
        env = os.environ.copy()
        make_args = ["make", "px4_sitl", self._config.target]
        self._process = subprocess.Popen(  # nosec B603 — argv list, cwd from env config
            make_args,
            cwd=str(self._config.px4_autopilot_dir),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return True

    def stop(self) -> None:
        if self._process is None:
            return
        try:
            self._process.send_signal(signal.SIGTERM)
            self._process.wait(timeout=15)
        except (subprocess.TimeoutExpired, ProcessLookupError):
            try:
                self._process.kill()
            except ProcessLookupError:
                pass
        self._process = None


def _config_from_env() -> SitlLauncherConfig:
    root = os.environ.get("PX4_AUTOPILOT_DIR", "")
    path = Path(root) if root else Path.home() / "PX4-Autopilot"
    return SitlLauncherConfig(px4_autopilot_dir=path)