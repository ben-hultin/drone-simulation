"""Protocol for ULog metrics parsing (pyulog behind services/)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class UlgFlightMetrics:
    flight_time_s: float
    max_position_error_m: float


class UlgReader(Protocol):
    def parse(self, ulg_path: str) -> UlgFlightMetrics: ...