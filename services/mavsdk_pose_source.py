"""Vehicle pose from MAVSDK when ROS odometry is not bridged yet."""

import time

from services.mavsdk_service import MavsdkService
from services.perception_protocol import PoseSample


class MavsdkPoseSource:
    """Reads local position through MavsdkService (loopback SITL / MAVSDK path)."""

    def __init__(self, mavsdk: MavsdkService) -> None:
        self._mavsdk = mavsdk

    async def latest_pose(self) -> PoseSample | None:
        position = await self._mavsdk.read_position(timeout_s=1.0)
        if position is None:
            return None
        return PoseSample(
            north_m=position.north_m,
            east_m=position.east_m,
            alt_m=position.alt_m,
            stamp_monotonic_s=time.monotonic(),
        )