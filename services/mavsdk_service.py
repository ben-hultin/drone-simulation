"""MAVSDK vehicle I/O with explicit timeouts and arm fail-safe."""

import asyncio
import time

from services.mavsdk_protocol import (
    ArmAttemptResult,
    VehicleGateway,
    VehiclePosition,
)
from services.mavsdk_service_flight_util import within_tolerance
from services.mavsdk_service_util import is_vehicle_healthy, refuse_reason_for_health
from services.mavsdk_url_util import validate_connection_url

DEFAULT_MAVSDK_URL = "udpin://127.0.0.1:14540"
DEFAULT_CONNECT_TIMEOUT_S = 10.0
DEFAULT_HEALTH_TIMEOUT_S = 10.0
DEFAULT_COMMAND_TIMEOUT_S = 60.0


class MavsdkService:
    """Coordinates connect, health check, and guarded arm evaluation through a gateway."""

    def __init__(
        self,
        gateway: VehicleGateway,
        connection_url: str = DEFAULT_MAVSDK_URL,
        *,
        allow_wildcard_bind: bool = False,
        allow_remote: bool = False,
    ) -> None:
        self._gateway = gateway
        self.connection_url = validate_connection_url(
            connection_url,
            allow_wildcard_bind=allow_wildcard_bind,
            allow_remote=allow_remote,
        )
        self._connected = False

    async def connect_or_fail(self, timeout_s: float = DEFAULT_CONNECT_TIMEOUT_S) -> bool:
        """Wait for MAVLink connection; return False on timeout (fail-safe)."""
        self._connected = await self._gateway.wait_for_connection(timeout_s)
        return self._connected

    async def verify_health_or_fail(
        self,
        timeout_s: float = DEFAULT_HEALTH_TIMEOUT_S,
    ) -> bool:
        """Return True when health flags satisfy pre-arm requirements."""
        if not self._connected:
            return False
        try:
            async with asyncio.timeout(timeout_s):
                health = await self._gateway.get_health()
        except TimeoutError:
            return False
        return is_vehicle_healthy(health)

    async def evaluate_arm_guard(
        self,
        timeout_s: float = DEFAULT_HEALTH_TIMEOUT_S,
    ) -> ArmAttemptResult:
        """Fail-safe arm guard for connectivity checks — does not command arm."""
        if not self._connected:
            return ArmAttemptResult(armed=False, refused=True, reason="not_connected")
        try:
            async with asyncio.timeout(timeout_s):
                health = await self._gateway.get_health()
        except TimeoutError:
            return ArmAttemptResult(armed=False, refused=True, reason="health_timeout")
        if not is_vehicle_healthy(health):
            return ArmAttemptResult(
                armed=False,
                refused=True,
                reason=refuse_reason_for_health(health),
            )
        return ArmAttemptResult(armed=False, refused=False, reason="arm_eligible")

    async def arm_or_fail(self, timeout_s: float = DEFAULT_COMMAND_TIMEOUT_S) -> bool:
        if not self._connected:
            return False
        try:
            async with asyncio.timeout(timeout_s):
                await self._gateway.arm()
        except (TimeoutError, OSError, RuntimeError):
            return False
        return True

    async def takeoff_or_fail(
        self,
        altitude_m: float,
        *,
        tolerance_m: float = 1.0,
        timeout_s: float = DEFAULT_COMMAND_TIMEOUT_S,
    ) -> bool:
        cmd_budget = min(15.0, timeout_s * 0.3)
        if not await self._run_command(
            lambda: self._gateway.takeoff(altitude_m),
            timeout_s=cmd_budget,
            failsafe_if_inflight=True,
        ):
            return False
        return await self._wait_at_waypoint(
            0.0,
            0.0,
            altitude_m,
            tolerance_m=tolerance_m,
            timeout_s=max(0.1, timeout_s - cmd_budget),
        )

    async def goto_or_fail(
        self,
        north_m: float,
        east_m: float,
        altitude_m: float,
        *,
        tolerance_m: float,
        timeout_s: float = DEFAULT_COMMAND_TIMEOUT_S,
    ) -> bool:
        cmd_budget = min(10.0, timeout_s * 0.25)
        moved = await self._run_command(
            lambda: self._gateway.goto_local(north_m, east_m, altitude_m),
            timeout_s=cmd_budget,
            failsafe_if_inflight=True,
        )
        if not moved:
            return False
        return await self._wait_at_waypoint(
            north_m,
            east_m,
            altitude_m,
            tolerance_m=tolerance_m,
            timeout_s=max(0.1, timeout_s - cmd_budget),
        )

    async def land_or_fail(self, timeout_s: float = DEFAULT_COMMAND_TIMEOUT_S) -> bool:
        return await self._run_command(
            lambda: self._gateway.land(),
            timeout_s=timeout_s,
            failsafe_if_inflight=True,
        )

    async def disarm_or_fail(self, timeout_s: float = DEFAULT_COMMAND_TIMEOUT_S) -> bool:
        return await self._run_command(lambda: self._gateway.disarm(), timeout_s=timeout_s)

    async def wait_landed_or_fail(self, timeout_s: float = DEFAULT_COMMAND_TIMEOUT_S) -> bool:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            flags = await self._read_flags_safe()
            if flags is not None and flags.landed:
                return True
            await asyncio.sleep(0.1)
        return False

    async def abort_inflight_failsafe(self) -> None:
        await self._failsafe_land()

    async def read_position(
        self,
        timeout_s: float = DEFAULT_HEALTH_TIMEOUT_S,
    ) -> VehiclePosition | None:
        if not self._connected:
            return None
        try:
            async with asyncio.timeout(timeout_s):
                return await self._gateway.get_position()
        except TimeoutError:
            return None

    async def read_failsafe(self, timeout_s: float = DEFAULT_HEALTH_TIMEOUT_S) -> bool:
        flags = await self._read_flags_safe(timeout_s=timeout_s)
        if flags is None:
            return True
        return flags.failsafe_triggered

    async def _read_flags_safe(
        self,
        timeout_s: float = DEFAULT_HEALTH_TIMEOUT_S,
    ):
        if not self._connected:
            return None
        try:
            async with asyncio.timeout(timeout_s):
                return await self._gateway.get_flight_flags()
        except (TimeoutError, OSError, RuntimeError):
            return None

    async def copy_ulg_path(self) -> str | None:
        path = await self._gateway.latest_ulg_path()
        return None if path is None else str(path)

    async def _wait_at_waypoint(
        self,
        north_m: float,
        east_m: float,
        altitude_m: float,
        *,
        tolerance_m: float,
        timeout_s: float,
    ) -> bool:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            position = await self.read_position(timeout_s=min(1.0, timeout_s))
            if position and within_tolerance(position, north_m, east_m, altitude_m, tolerance_m):
                return True
            await asyncio.sleep(0.05)
        await self._failsafe_land()
        return False

    async def _run_command(
        self,
        action,
        timeout_s: float,
        *,
        failsafe_if_inflight: bool = False,
    ) -> bool:
        if not self._connected:
            return False
        try:
            async with asyncio.timeout(timeout_s):
                await action()
        except (TimeoutError, OSError, RuntimeError):
            if failsafe_if_inflight:
                await self._failsafe_land()
            return False
        return True

    async def _failsafe_land(self) -> None:
        flags = await self._read_flags_safe()
        if flags is not None and not flags.in_air and not flags.armed:
            return
        await self._safe_gateway_call(self._gateway.return_to_launch)
        await self._safe_gateway_call(self._gateway.land)

    async def _safe_gateway_call(self, action) -> None:
        try:
            await action()
        except (TimeoutError, OSError, RuntimeError, ValueError, TypeError):
            return