"""Tests for MAVSDK-backed pose source."""

import asyncio
import time

from services.fake_gateway import FakeGateway
from services.mavsdk_pose_source import MavsdkPoseSource
from services.mavsdk_service import MavsdkService


def test_mavsdk_pose_source_reads_gateway() -> None:
    gateway = FakeGateway(connects=True)
    gateway._position = gateway._position  # default 0,0,0

    async def _run() -> None:
        service = MavsdkService(gateway)
        await service.connect_or_fail(1.0)
        source = MavsdkPoseSource(service)
        pose = await source.latest_pose()
        assert pose is not None
        assert pose.stamp_monotonic_s <= time.monotonic()

    asyncio.run(_run())