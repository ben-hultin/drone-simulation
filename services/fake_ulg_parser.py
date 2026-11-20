"""Stub ULog reader for hermetic tests."""

from dao.flight_log.ulg_reader_protocol import UlgFlightMetrics, UlgReader


class FakeUlgReader(UlgReader):
    def __init__(
        self,
        *,
        flight_time_s: float = 42.0,
        max_position_error_m: float = 0.25,
    ) -> None:
        self._flight_time_s = flight_time_s
        self._max_position_error_m = max_position_error_m
        self.parsed_paths: list[str] = []

    def parse(self, ulg_path: str) -> UlgFlightMetrics:
        self.parsed_paths.append(ulg_path)
        return UlgFlightMetrics(
            flight_time_s=self._flight_time_s,
            max_position_error_m=self._max_position_error_m,
        )