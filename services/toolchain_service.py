"""External toolchain presence checks (PX4, Gazebo, ROS 2 on PATH)."""

import shutil
from dataclasses import dataclass


def _which(name: str) -> str | None:
    return shutil.which(name)


@dataclass(frozen=True)
class ToolchainReport:
    """Toolchain availability for SITL live verification."""

    px4_on_path: bool
    gazebo_on_path: bool
    ros2_on_path: bool

    @property
    def ready_for_sitl(self) -> bool:
        return self.px4_on_path and self.gazebo_on_path and self.ros2_on_path


def probe_toolchain() -> ToolchainReport:
    """Inspect PATH without installing or starting simulators."""
    return ToolchainReport(
        px4_on_path=_which("px4") is not None,
        gazebo_on_path=_which("gz") is not None,
        ros2_on_path=_which("ros2") is not None,
    )