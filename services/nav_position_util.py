"""Shared local position math (used by service and fake gateway)."""

from services.mavsdk_protocol import VehiclePosition


def distance_to_waypoint(
    position: VehiclePosition,
    north_m: float,
    east_m: float,
    altitude_m: float,
) -> float:
    dn = position.north_m - north_m
    de = position.east_m - east_m
    da = position.alt_m - altitude_m
    return (dn * dn + de * de + da * da) ** 0.5


def position_at_waypoint(north_m: float, east_m: float, altitude_m: float) -> VehiclePosition:
    return VehiclePosition(north_m=north_m, east_m=east_m, alt_m=altitude_m)