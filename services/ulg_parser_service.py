"""Parse PX4 ULog files via pyulog when available."""

from dao.flight_log.ulg_reader_protocol import UlgFlightMetrics, UlgReader


class UlgParserService(UlgReader):
    """Production ULog parser using pyulog."""

    def parse(self, ulg_path: str) -> UlgFlightMetrics:
        from pyulog import ULog

        log = ULog(ulg_path)
        start_us = log.start_timestamp
        end_us = log.last_timestamp
        flight_time_s = max(0.0, (end_us - start_us) / 1_000_000.0)
        max_err = _max_position_error_from_log(log)
        return UlgFlightMetrics(flight_time_s=flight_time_s, max_position_error_m=max_err)


def _max_position_error_from_log(log) -> float:
    dataset = log.get_dataset("vehicle_local_position")
    if dataset is None:
        return 0.0
    data = dataset.data
    if "x" not in data or "y" not in data:
        return 0.0
    xs = data["x"]
    ys = data["y"]
    if len(xs) == 0:
        return 0.0
    return max((float(x) ** 2 + float(y) ** 2) ** 0.5 for x, y in zip(xs, ys, strict=False))