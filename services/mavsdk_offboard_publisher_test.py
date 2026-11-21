"""Tests for MAVSDK offboard publisher boundary."""

import asyncio

from services.fake_gateway import FakeGateway
from services.mavsdk_offboard_publisher import MavsdkOffboardPublisher
from services.offboard_command_protocol import OffboardSetpoint


def test_publish_moves_gateway() -> None:
    gateway = FakeGateway(connects=True)
    publisher = MavsdkOffboardPublisher(gateway)

    async def _run() -> None:
        await gateway.arm()
        await publisher.enable_offboard()
        assert gateway._offboard_active is True
        await publisher.publish_setpoint(OffboardSetpoint(1.0, 2.0, 5.0))

    asyncio.run(_run())
    assert gateway.goto_calls == [(1.0, 2.0, 5.0)]