"""Fail-safe paths on MavsdkService."""

import asyncio

from services.fake_gateway import FakeGateway
from services.mavsdk_service import MavsdkService


class LandRaisesGateway(FakeGateway):
    async def land(self) -> None:
        raise RuntimeError("land_failed")


def test_takeoff_when_not_connected() -> None:
    service = MavsdkService(FakeGateway(connects=False))
    assert asyncio.run(service.takeoff_or_fail(5.0)) is False


def test_failsafe_land_swallows_gateway_errors() -> None:
    gateway = LandRaisesGateway()
    service = MavsdkService(gateway)
    asyncio.run(service.connect_or_fail())
    asyncio.run(service.arm_or_fail())
    assert asyncio.run(service.land_or_fail()) is False