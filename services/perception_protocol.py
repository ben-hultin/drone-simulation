"""Pose and depth inputs for Phase 2 perception (no ROS import)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PoseSample:
    """Vehicle pose in local NED (meters)."""

    north_m: float
    east_m: float
    alt_m: float
    stamp_monotonic_s: float


@dataclass(frozen=True)
class DepthFrame:
    """Rectified depth image in meters (row-major)."""

    width: int
    height: int
    depths_m: tuple[float, ...]
    stamp_monotonic_s: float
    fx: float = 525.0
    fy: float = 525.0
    cx: float | None = None
    cy: float | None = None


@dataclass(frozen=True)
class Point3:
    x_m: float
    y_m: float
    z_m: float


@dataclass(frozen=True)
class PointCloud:
    points: tuple[Point3, ...]
    frame_id: str = "camera_depth"


class PoseSource(Protocol):
    """Injectable boundary for /fmu/out/vehicle_odometry or equivalent."""

    async def latest_pose(self) -> PoseSample | None: ...


class DepthSource(Protocol):
    """Injectable boundary for bridged Gazebo depth camera."""

    async def latest_depth(self) -> DepthFrame | None: ...