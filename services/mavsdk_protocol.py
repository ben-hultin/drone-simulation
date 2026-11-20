"""Protocols and types for MAVSDK vehicle access (no mavsdk import)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class VehiclePosition:
    """Local NED-style position relative to home (meters; up positive)."""

    north_m: float
    east_m: float
    alt_m: float


@dataclass(frozen=True)
class VehicleFlightFlags:
    """Telemetry flags for landing and failsafe checks."""

    in_air: bool
    failsafe_triggered: bool
    landed: bool
    armed: bool


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

    async def takeoff(self, altitude_m: float) -> None: ...

    async def goto_local(self, north_m: float, east_m: float, altitude_m: float) -> None: ...

    async def land(self) -> None: ...

    async def disarm(self) -> None: ...

    async def get_position(self) -> VehiclePosition: ...

    async def get_flight_flags(self) -> VehicleFlightFlags: ...

    async def return_to_launch(self) -> None: ...

    async def latest_ulg_path(self) -> Path | None: ...

    async def close(self) -> None: ...