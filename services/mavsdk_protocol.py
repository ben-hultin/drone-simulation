"""Protocols and types for MAVSDK vehicle access (no mavsdk import)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VehicleHealth:
    """Snapshot of vehicle health flags from the autopilot."""

    is_armable: bool
    is_global_position_ok: bool
    is_home_position_ok: bool
    is_local_position_ok: bool


@dataclass(frozen=True)
class ArmAttemptResult:
    """Outcome of an arm attempt with fail-safe refusal reason."""

    armed: bool
    refused: bool
    reason: str


class VehicleGateway(Protocol):
    """Injectable boundary for MAVSDK; mocked in tests."""

    async def wait_for_connection(self, timeout_s: float) -> bool: ...

    async def get_health(self) -> VehicleHealth: ...

    async def arm(self) -> None: ...

    async def close(self) -> None: ...