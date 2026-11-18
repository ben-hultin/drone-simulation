"""MAVSDK vehicle I/O with explicit timeouts and arm fail-safe."""

import asyncio

from services.mavsdk_protocol import ArmAttemptResult, VehicleGateway
from services.mavsdk_service_util import is_vehicle_healthy, refuse_reason_for_health
from services.mavsdk_url_util import validate_connection_url

DEFAULT_MAVSDK_URL = "udpin://127.0.0.1:14540"
DEFAULT_CONNECT_TIMEOUT_S = 10.0
DEFAULT_HEALTH_TIMEOUT_S = 10.0


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