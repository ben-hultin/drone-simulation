"""Helpers for SITL connectivity mission results."""

from missions.sitl_connectivity_types import SitlConnectivityResult, SitlConnectivityStatus
from services.mavsdk_protocol import ArmAttemptResult


def result_payload(result: SitlConnectivityResult) -> dict[str, str | bool]:
    """Serialize a mission result for the mission log DAO."""
    return {
        "status": result.status.value,
        "endpoint": result.endpoint,
        "arm_refused": result.arm_refused,
        "reason": result.reason,
    }


def status_from_arm_guard(guard: ArmAttemptResult) -> SitlConnectivityStatus:
    """Map arm guard outcome to mission status."""
    if guard.reason == "not_connected":
        return SitlConnectivityStatus.UNREACHABLE
    if guard.refused:
        return SitlConnectivityStatus.UNHEALTHY
    return SitlConnectivityStatus.READY