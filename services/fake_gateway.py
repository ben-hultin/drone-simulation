"""Test double for VehicleGateway (services boundary only)."""

from services.mavsdk_protocol import VehicleHealth


class FakeGateway:
    def __init__(
        self,
        *,
        connects: bool = True,
        health: VehicleHealth | None = None,
        arm_raises: Exception | None = None,
    ) -> None:
        self._connects = connects
        self._health = health or VehicleHealth(
            is_armable=True,
            is_global_position_ok=True,
            is_home_position_ok=True,
            is_local_position_ok=True,
        )
        self._arm_raises = arm_raises
        self.arm_called = False

    async def wait_for_connection(self, timeout_s: float) -> bool:
        del timeout_s
        return self._connects

    async def get_health(self) -> VehicleHealth:
        return self._health

    async def arm(self) -> None:
        self.arm_called = True
        if self._arm_raises:
            raise self._arm_raises

    async def close(self) -> None:
        return None