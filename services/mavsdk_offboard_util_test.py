"""Tests for offboard message builder."""

from services.mavsdk_offboard_util import build_position_ned_yaw


def test_build_position_ned_yaw() -> None:
    msg = build_position_ned_yaw(1.0, 2.0, -3.0, 0.0)
    assert msg.north_m == 1.0