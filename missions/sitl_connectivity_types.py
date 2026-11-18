"""Types for SITL connectivity mission."""

from dataclasses import dataclass
from enum import StrEnum


class SitlConnectivityStatus(StrEnum):
    UNREACHABLE = "unreachable"
    UNHEALTHY = "unhealthy"
    READY = "ready"


@dataclass(frozen=True)
class SitlConnectivityResult:
    status: SitlConnectivityStatus
    endpoint: str
    arm_refused: bool
    reason: str
    logged: bool