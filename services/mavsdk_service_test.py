"""Tests for MAVSDK service fail-safe behavior."""

import asyncio

from services.fake_gateway import FakeGateway
from services.mavsdk_protocol import VehicleHealth
from services.mavsdk_service import DEFAULT_MAVSDK_URL, MavsdkService


class SlowHealthGateway(FakeGateway):
    async def get_health(self) -> VehicleHealth:
        await asyncio.sleep(5.0)
        return await super().get_health()


def test_connect_succeeds_within_timeout() -> None:
    service = MavsdkService(FakeGateway(connects=True))
    assert asyncio.run(service.connect_or_fail(timeout_s=1.0)) is True


def test_connect_timeout_fails_safe() -> None:
    service = MavsdkService(FakeGateway(connects=False))
    assert asyncio.run(service.connect_or_fail(timeout_s=0.1)) is False


def test_unhealthy_vehicle_refuses_arm_guard() -> None:
    bad = VehicleHealth(
        is_armable=False,
        is_global_position_ok=False,
        is_home_position_ok=True,
        is_local_position_ok=True,
    )
    gateway = FakeGateway(health=bad)
    service = MavsdkService(gateway)
    assert asyncio.run(service.connect_or_fail(timeout_s=1.0)) is True
    result = asyncio.run(service.evaluate_arm_guard())
    assert result.refused is True
    assert gateway.arm_called is False


def test_healthy_vehicle_arm_eligible_without_command() -> None:
    gateway = FakeGateway()
    service = MavsdkService(gateway)
    asyncio.run(service.connect_or_fail(timeout_s=1.0))
    result = asyncio.run(service.evaluate_arm_guard())
    assert result.refused is False
    assert result.reason == "arm_eligible"
    assert gateway.arm_called is False


def test_default_connection_url() -> None:
    assert DEFAULT_MAVSDK_URL == "udpin://127.0.0.1:14540"


def test_verify_health_fails_when_not_connected() -> None:
    service = MavsdkService(FakeGateway(connects=False))
    assert asyncio.run(service.verify_health_or_fail()) is False


def test_verify_health_timeout() -> None:
    service = MavsdkService(SlowHealthGateway())
    asyncio.run(service.connect_or_fail(timeout_s=1.0))
    assert asyncio.run(service.verify_health_or_fail(timeout_s=0.01)) is False


def test_arm_guard_refused_when_not_connected() -> None:
    service = MavsdkService(FakeGateway(connects=False))
    result = asyncio.run(service.evaluate_arm_guard())
    assert result.refused is True
    assert result.reason == "not_connected"


def test_arm_guard_health_timeout() -> None:
    service = MavsdkService(SlowHealthGateway())
    asyncio.run(service.connect_or_fail(timeout_s=1.0))
    result = asyncio.run(service.evaluate_arm_guard(timeout_s=0.01))
    assert result.refused is True
    assert result.reason == "health_timeout"