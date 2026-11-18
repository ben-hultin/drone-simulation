"""Helpers for MAVSDK service health checks."""

from services.mavsdk_protocol import VehicleHealth


def is_vehicle_healthy(health: VehicleHealth) -> bool:
    """Return True when required health flags report OK for a safe arm attempt."""
    return (
        health.is_armable
        and health.is_global_position_ok
        and health.is_home_position_ok
        and health.is_local_position_ok
    )


def refuse_reason_for_health(health: VehicleHealth) -> str:
    """Human-readable reason when arm must be refused."""
    if not health.is_armable:
        return "vehicle_not_armable"
    if not health.is_global_position_ok:
        return "global_position_unhealthy"
    if not health.is_home_position_ok:
        return "home_position_unhealthy"
    if not health.is_local_position_ok:
        return "local_position_unhealthy"
    return "unknown_unhealthy"