"""PX4 offboard setpoints via MAVSDK (services boundary)."""

from services.mavsdk_protocol import VehicleGateway
from services.offboard_command_protocol import OffboardSetpoint


class MavsdkOffboardPublisher:
    """Maps OffboardSetpoint messages to gateway local setpoints."""

    def __init__(self, gateway: VehicleGateway) -> None:
        self._gateway = gateway
        self._enabled = False

    async def enable_offboard(self) -> None:
        await self._gateway.offboard_start()
        self._enabled = True

    async def publish_setpoint(self, setpoint: OffboardSetpoint) -> None:
        if not self._enabled:
            raise RuntimeError("offboard_not_enabled")
        await self._gateway.goto_local(setpoint.north_m, setpoint.east_m, setpoint.alt_m)

    async def disable_offboard(self) -> None:
        await self._gateway.offboard_stop()
        self._enabled = False