"""Hold verification using telemetry only (no duplicate offboard commands)."""

import asyncio
import time

from services.mavsdk_protocol import VehiclePosition
from services.mavsdk_service import MavsdkService
from services.mavsdk_service_flight_util import within_tolerance


async def wait_at_position(
    mavsdk: MavsdkService,
    target: VehiclePosition,
    *,
    tolerance_m: float,
    timeout_s: float,
) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        position = await mavsdk.read_position(timeout_s=min(1.0, timeout_s))
        if position and within_tolerance(
            position,
            target.north_m,
            target.east_m,
            target.alt_m,
            tolerance_m,
        ):
            return True
        await asyncio.sleep(0.05)
    return False