"""PX4 offboard setpoint publishing (ROS XRCE or MAVSDK behind services/)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class OffboardSetpoint:
    """Local NED position setpoint (altitude positive up in alt_m field)."""

    north_m: float
    east_m: float
    alt_m: float
    yaw_deg: float = 0.0


class OffboardPublisher(Protocol):
    """Publishes OffboardControlMode + TrajectorySetpoint equivalents."""

    async def enable_offboard(self) -> None: ...

    async def publish_setpoint(self, setpoint: OffboardSetpoint) -> None: ...

    async def disable_offboard(self) -> None: ...