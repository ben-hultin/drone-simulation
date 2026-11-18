"""Tests for SITL connectivity helpers."""

from missions.sitl_connectivity_types import SitlConnectivityResult, SitlConnectivityStatus
from missions.sitl_connectivity_util import result_payload, status_from_arm_guard
from services.mavsdk_protocol import ArmAttemptResult


def test_status_unreachable() -> None:
    guard = ArmAttemptResult(armed=False, refused=True, reason="not_connected")
    assert status_from_arm_guard(guard) == SitlConnectivityStatus.UNREACHABLE


def test_status_unhealthy() -> None:
    guard = ArmAttemptResult(armed=False, refused=True, reason="health_timeout")
    assert status_from_arm_guard(guard) == SitlConnectivityStatus.UNHEALTHY


def test_status_ready() -> None:
    guard = ArmAttemptResult(armed=False, refused=False, reason="arm_eligible")
    assert status_from_arm_guard(guard) == SitlConnectivityStatus.READY


def test_result_payload_serializes_status() -> None:
    result = SitlConnectivityResult(
        status=SitlConnectivityStatus.READY,
        endpoint="udpin://127.0.0.1:14540",
        arm_refused=False,
        reason="arm_eligible",
        logged=True,
    )
    payload = result_payload(result)
    assert payload["status"] == "ready"