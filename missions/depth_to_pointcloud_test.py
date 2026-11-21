"""Integration test for depth converter wrapper."""

import time

from missions.depth_to_pointcloud import DepthToPointCloudConverter
from services.perception_protocol import DepthFrame


def test_converter_delegates_to_util() -> None:
    frame = DepthFrame(
        width=2,
        height=1,
        depths_m=(2.0, 2.0),
        stamp_monotonic_s=time.monotonic(),
    )
    cloud = DepthToPointCloudConverter().convert(frame)
    assert len(cloud.points) == 2