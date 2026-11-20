"""Tests for MavsdkService flight commands."""

import asyncio

from services.fake_gateway import FakeGateway
from services.mavsdk_service import MavsdkService


def test_arm_or_fail_commands_gateway() -> None:
    gateway = FakeGateway()
    service = MavsdkService(gateway)
    asyncio.run(service.connect_or_fail(timeout_s=1.0))
    assert asyncio.run(service.arm_or_fail()) is True
    assert gateway.arm_called is True


def test_goto_or_fail_within_tolerance() -> None:
    gateway = FakeGateway()
    service = MavsdkService(gateway)
    asyncio.run(service.connect_or_fail(timeout_s=1.0))
    asyncio.run(service.arm_or_fail())
    asyncio.run(service.takeoff_or_fail(5.0, tolerance_m=1.0))
    ok = asyncio.run(service.goto_or_fail(5.0, 0.0, 5.0, tolerance_m=1.0, timeout_s=2.0))
    assert ok is True