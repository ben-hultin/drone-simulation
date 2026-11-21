"""Result types for offboard hover mission."""

from dataclasses import dataclass
from enum import StrEnum


class OffboardHoverStatus(StrEnum):
    SUCCESS = "success"
    CONNECT_FAILED = "connect_failed"
    HEALTH_FAILED = "health_failed"
    ARM_FAILED = "arm_failed"
    POSE_TIMEOUT = "pose_timeout"
    DEPTH_TIMEOUT = "depth_timeout"
    OFFBOARD_FAILED = "offboard_failed"
    TAKEOFF_FAILED = "takeoff_failed"
    HOVER_FAILED = "hover_failed"
    LAND_FAILED = "land_failed"
    DISARM_FAILED = "disarm_failed"
    FAILSAFE = "failsafe"
    TIME_LIMIT = "time_limit"


@dataclass(frozen=True)
class OffboardHoverResult:
    status: OffboardHoverStatus
    reason: str
    point_count: int = 0
    hover_setpoints_published: int = 0
    ulg_saved: bool = False
    rosbag_recorded: bool = False