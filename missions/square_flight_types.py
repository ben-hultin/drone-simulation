"""Result types for square flight mission."""

from dataclasses import dataclass
from enum import StrEnum


class SquareFlightStatus(StrEnum):
    SUCCESS = "success"
    CONNECT_FAILED = "connect_failed"
    ARM_FAILED = "arm_failed"
    TAKEOFF_FAILED = "takeoff_failed"
    WAYPOINT_FAILED = "waypoint_failed"
    LAND_FAILED = "land_failed"
    DISARM_FAILED = "disarm_failed"
    FAILSAFE = "failsafe"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class SquareFlightResult:
    status: SquareFlightStatus
    reason: str
    waypoints_reached: int
    ulg_saved: bool
    metrics_recorded: bool