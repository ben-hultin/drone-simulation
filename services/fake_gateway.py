"""Test double for VehicleGateway (services boundary only)."""

from pathlib import Path

from services.fake_gateway_flight_util import position_at_waypoint
from services.mavsdk_protocol import VehicleFlightFlags, VehicleHealth, VehiclePosition


class FakeGateway:
    def __init__(
        self,
        *,
        connects: bool = True,
        health: VehicleHealth | None = None,
        arm_raises: Exception | None = None,
        failsafe: bool = False,
        ulg_path: Path | None = None,
        position: VehiclePosition | None = None,
    ) -> None:
        self._connects = connects
        self._health = health or VehicleHealth(
            is_armable=True,
            is_global_position_ok=True,
            is_home_position_ok=True,
            is_local_position_ok=True,
        )
        self._arm_raises = arm_raises
        self._failsafe = failsafe
        self._ulg_path = ulg_path
        self._position = position or VehiclePosition(north_m=0.0, east_m=0.0, alt_m=0.0)
        self._armed = False
        self._in_air = False
        self.arm_called = False
        self.land_called = False
        self.disarm_called = False
        self.rtl_called = False
        self.goto_calls: list[tuple[float, float, float]] = []

    async def wait_for_connection(self, timeout_s: float) -> bool:
        del timeout_s
        return self._connects

    async def get_health(self) -> VehicleHealth:
        return self._health

    async def arm(self) -> None:
        self.arm_called = True
        if self._arm_raises:
            raise self._arm_raises
        self._armed = True

    async def takeoff(self, altitude_m: float) -> None:
        if not self._armed:
            raise RuntimeError("not_armed")
        self._in_air = True
        self._position = position_at_waypoint(0.0, 0.0, altitude_m)

    async def goto_local(self, north_m: float, east_m: float, altitude_m: float) -> None:
        self.goto_calls.append((north_m, east_m, altitude_m))
        self._position = position_at_waypoint(north_m, east_m, altitude_m)

    async def land(self) -> None:
        self.land_called = True
        self._in_air = False
        self._position = position_at_waypoint(
            self._position.north_m,
            self._position.east_m,
            0.0,
        )

    async def disarm(self) -> None:
        self.disarm_called = True
        self._armed = False

    async def get_position(self) -> VehiclePosition:
        return self._position

    async def get_flight_flags(self) -> VehicleFlightFlags:
        return VehicleFlightFlags(
            in_air=self._in_air,
            failsafe_triggered=self._failsafe,
            landed=not self._in_air,
            armed=self._armed,
        )

    async def return_to_launch(self) -> None:
        self.rtl_called = True
        self._position = position_at_waypoint(0.0, 0.0, self._position.alt_m)

    async def latest_ulg_path(self) -> Path | None:
        return self._ulg_path

    async def close(self) -> None:
        return None