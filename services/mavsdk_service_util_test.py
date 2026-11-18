"""Tests for MAVSDK service helpers."""

from services.mavsdk_protocol import VehicleHealth
from services.mavsdk_service_util import is_vehicle_healthy, refuse_reason_for_health


def test_is_vehicle_healthy_all_ok() -> None:
    health = VehicleHealth(True, True, True, True)
    assert is_vehicle_healthy(health) is True


def test_is_vehicle_healthy_missing_flag() -> None:
    health = VehicleHealth(True, True, True, False)
    assert is_vehicle_healthy(health) is False


def test_refuse_reason_not_armable() -> None:
    health = VehicleHealth(False, True, True, True)
    assert refuse_reason_for_health(health) == "vehicle_not_armable"


def test_refuse_reason_global_position() -> None:
    health = VehicleHealth(True, False, True, True)
    assert refuse_reason_for_health(health) == "global_position_unhealthy"


def test_refuse_reason_home_position() -> None:
    health = VehicleHealth(True, True, False, True)
    assert refuse_reason_for_health(health) == "home_position_unhealthy"


def test_refuse_reason_local_position() -> None:
    health = VehicleHealth(True, True, True, False)
    assert refuse_reason_for_health(health) == "local_position_unhealthy"