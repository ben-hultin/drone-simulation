"""Test doubles for pose and depth sources (services boundary)."""

import time

from services.perception_protocol import DepthFrame, PoseSample


class FakePoseSource:
    def __init__(
        self,
        *,
        pose: PoseSample | None = None,
        return_none: bool = False,
    ) -> None:
        self._return_none = return_none
        if pose is None and not return_none:
            now = time.monotonic()
            pose = PoseSample(north_m=0.0, east_m=0.0, alt_m=0.0, stamp_monotonic_s=now)
        self._pose = pose

    def set_pose(self, pose: PoseSample) -> None:
        self._pose = pose

    async def latest_pose(self) -> PoseSample | None:
        if self._return_none:
            return None
        return self._pose


class FakeDepthSource:
    def __init__(
        self,
        *,
        frame: DepthFrame | None = None,
        return_none: bool = False,
    ) -> None:
        self._return_none = return_none
        if frame is None and not return_none:
            now = time.monotonic()
            frame = _default_depth_frame(now)
        self._frame = frame

    def set_frame(self, frame: DepthFrame) -> None:
        self._frame = frame

    async def latest_depth(self) -> DepthFrame | None:
        if self._return_none:
            return None
        return self._frame


def _default_depth_frame(stamp: float) -> DepthFrame:
    w, h = 4, 3
    depths = tuple(2.0 + (i % 3) * 0.1 for i in range(w * h))
    return DepthFrame(width=w, height=h, depths_m=depths, stamp_monotonic_s=stamp)