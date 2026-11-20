"""Tests for flight waypoint helpers."""

from services.mavsdk_protocol import VehiclePosition
from services.mavsdk_service_flight_util import within_tolerance


def test_within_tolerance() -> None:
    pos = VehiclePosition(north_m=5.0, east_m=0.0, alt_m=5.0)
    assert within_tolerance(pos, 5.0, 0.0, 5.0, 1.0) is True