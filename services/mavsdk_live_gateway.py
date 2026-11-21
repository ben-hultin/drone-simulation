"""MAVSDK System implementation of VehicleGateway."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from services.mavsdk_offboard_util import build_position_ned_yaw
from services.mavsdk_protocol import VehicleFlightFlags, VehicleHealth, VehiclePosition
from services.mavsdk_url_util import validate_connection_url

if TYPE_CHECKING:
    from mavsdk_grpc.system import System

DEFAULT_TELEMETRY_TIMEOUT_S = 10.0


class MavsdkLiveGateway:
    """Wraps MAVSDK System; lazy-imports mavsdk_grpc only for live flight."""

    def __init__(self, connection_url: str, *, allow_remote: bool = False) -> None:
        self._connection_url = validate_connection_url(
            connection_url,
            allow_remote=allow_remote,
        )
        self._system: System | None = None
        self._offboard_active = False

    async def wait_for_connection(self, timeout_s: float) -> bool:
        await self.close()
        import mavsdk_grpc as mavsdk

        system = mavsdk.System()
        try:
            async with asyncio.timeout(timeout_s):
                await system.connect(self._connection_url)
                async for state in system.core.connection_state():
                    if state.is_connected:
                        self._system = system
                        return True
        except (TimeoutError, OSError, RuntimeError):
            await self._release_system(system)
            return False
        except Exception:
            await self._release_system(system)
            raise
        await self._release_system(system)
        return False

    async def get_health(self) -> VehicleHealth:
        system = self._require_connected_system()
        try:
            async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
                async for health in system.telemetry.health():
                    return VehicleHealth(
                        is_armable=health.is_armable,
                        is_global_position_ok=health.is_global_position_ok,
                        is_home_position_ok=health.is_home_position_ok,
                        is_local_position_ok=health.is_local_position_ok,
                    )
        except TimeoutError:
            raise
        raise TimeoutError("health_stream_empty")

    async def arm(self) -> None:
        system = self._require_connected_system()
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            await system.action.arm()

    async def takeoff(self, altitude_m: float) -> None:
        system = self._require_connected_system()
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            await system.action.set_takeoff_altitude(altitude_m)
            await system.action.takeoff()

    async def goto_local(self, north_m: float, east_m: float, altitude_m: float) -> None:
        system = self._require_connected_system()
        target = build_position_ned_yaw(north_m, east_m, -altitude_m, 0.0)
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            await system.offboard.set_position_ned(target)
            if not self._offboard_active:
                await system.offboard.start()
                self._offboard_active = True

    async def offboard_start(self) -> None:
        system = self._require_connected_system()
        target = build_position_ned_yaw(0.0, 0.0, 0.0, 0.0)
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            await system.offboard.set_position_ned(target)
            if not self._offboard_active:
                await system.offboard.start()
                self._offboard_active = True

    async def offboard_stop(self) -> None:
        if self._system is None:
            return
        await self._stop_offboard(self._system)

    async def land(self) -> None:
        system = self._require_connected_system()
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            await self._stop_offboard(system)
            await system.action.land()

    async def disarm(self) -> None:
        system = self._require_connected_system()
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            await system.action.disarm()

    async def get_position(self) -> VehiclePosition:
        system = self._require_connected_system()
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            async for pos in system.telemetry.position_velocity_ned():
                return VehiclePosition(
                    north_m=pos.position.north_m,
                    east_m=pos.position.east_m,
                    alt_m=-pos.position.down_m,
                )
        raise TimeoutError("position_stream_empty")

    async def get_flight_flags(self) -> VehicleFlightFlags:
        system = self._require_connected_system()
        in_air = False
        armed = False
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            async for armed_state in system.telemetry.armed():
                armed = armed_state
                break
            async for land in system.telemetry.in_air():
                in_air = land
                break
        failsafe = False
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            async for mode in system.telemetry.flight_mode():
                failsafe = str(mode).lower().find("return") >= 0
                break
        return VehicleFlightFlags(
            in_air=in_air,
            failsafe_triggered=failsafe,
            landed=not in_air,
            armed=armed,
        )

    async def return_to_launch(self) -> None:
        system = self._require_connected_system()
        async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
            await self._stop_offboard(system)
            await system.action.return_to_launch()

    async def latest_ulg_path(self) -> Path | None:
        from services.ulg_path_util import default_px4_log_root, newest_ulg_under

        return newest_ulg_under(default_px4_log_root())

    async def close(self) -> None:
        if self._system is not None:
            await self._stop_offboard(self._system)
            await self._release_system(self._system)

    async def _stop_offboard(self, system: System) -> None:
        if not self._offboard_active:
            return
        try:
            async with asyncio.timeout(DEFAULT_TELEMETRY_TIMEOUT_S):
                await system.offboard.stop()
        except (TimeoutError, OSError, RuntimeError):
            return
        self._offboard_active = False

    async def _release_system(self, system: System) -> None:
        try:
            await system.disconnect()
        except (AttributeError, OSError, RuntimeError):
            pass
        if self._system is system:
            self._system = None

    def _require_connected_system(self) -> System:
        if self._system is None:
            raise RuntimeError("mavsdk_not_connected")
        return self._system