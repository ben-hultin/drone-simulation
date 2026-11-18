"""MAVSDK System implementation of VehicleGateway."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from services.mavsdk_protocol import VehicleHealth
from services.mavsdk_url_util import validate_connection_url

if TYPE_CHECKING:
    from mavsdk.system import System

DEFAULT_TELEMETRY_TIMEOUT_S = 10.0


class MavsdkLiveGateway:
    """Wraps mavsdk.System; lazy-imports mavsdk only for live flight."""

    def __init__(self, connection_url: str, *, allow_remote: bool = False) -> None:
        self._connection_url = validate_connection_url(
            connection_url,
            allow_remote=allow_remote,
        )
        self._system: System | None = None

    async def wait_for_connection(self, timeout_s: float) -> bool:
        await self.close()
        from mavsdk import System

        system = System()
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

    async def close(self) -> None:
        if self._system is not None:
            await self._release_system(self._system)

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