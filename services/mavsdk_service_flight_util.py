"""Flight helpers for MavsdkService waypoint and fail-safe logic."""

from services.mavsdk_protocol import VehiclePosition
from services.nav_position_util import distance_to_waypoint


def within_tolerance(
    position: VehiclePosition,
    north_m: float,
    east_m: float,
    altitude_m: float,
    tolerance_m: float,
) -> bool:
    return distance_to_waypoint(position, north_m, east_m, altitude_m) <= tolerance_m