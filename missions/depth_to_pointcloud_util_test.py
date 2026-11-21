"""Tests for depth-to-point-cloud conversion."""

import pytest

from missions.depth_to_pointcloud_util import depth_frame_to_point_cloud, validate_depth_frame
from services.perception_protocol import DepthFrame


def test_depth_to_point_cloud_pinhole() -> None:
    frame = DepthFrame(
        width=2,
        height=2,
        depths_m=(1.0, 1.0, 2.0, 2.0),
        stamp_monotonic_s=0.0,
        fx=1.0,
        fy=1.0,
        cx=0.5,
        cy=0.5,
    )
    cloud = depth_frame_to_point_cloud(frame)
    assert len(cloud.points) == 4
    assert cloud.points[0].z_m == 1.0


def test_depth_to_point_cloud_skips_invalid() -> None:
    frame = DepthFrame(
        width=1,
        height=2,
        depths_m=(0.0, 1.5),
        stamp_monotonic_s=0.0,
    )
    cloud = depth_frame_to_point_cloud(frame)
    assert len(cloud.points) == 1


def test_validate_depth_frame_rejects_length_mismatch() -> None:
    frame = DepthFrame(width=2, height=2, depths_m=(1.0,), stamp_monotonic_s=0.0)
    with pytest.raises(ValueError, match="depth_frame_length"):
        validate_depth_frame(frame)