"""Depth image to point cloud (pinhole model)."""

from services.perception_protocol import DepthFrame, Point3, PointCloud

_MAX_DEPTH_PIXELS = 640 * 480


def validate_depth_frame(frame: DepthFrame) -> None:
    expected = frame.width * frame.height
    if frame.width <= 0 or frame.height <= 0 or expected > _MAX_DEPTH_PIXELS:
        raise ValueError("depth_frame_bounds")
    if len(frame.depths_m) != expected:
        raise ValueError("depth_frame_length")
    if frame.fx <= 0.0 or frame.fy <= 0.0:
        raise ValueError("depth_intrinsics")


def depth_frame_to_point_cloud(frame: DepthFrame, *, min_depth_m: float = 0.1) -> PointCloud:
    validate_depth_frame(frame)
    cx = frame.cx if frame.cx is not None else frame.width / 2.0
    cy = frame.cy if frame.cy is not None else frame.height / 2.0
    points: list[Point3] = []
    for row in range(frame.height):
        for col in range(frame.width):
            idx = row * frame.width + col
            depth = frame.depths_m[idx]
            if depth < min_depth_m:
                continue
            x = (col - cx) * depth / frame.fx
            y = (row - cy) * depth / frame.fy
            z = depth
            points.append(Point3(x_m=x, y_m=y, z_m=z))
    return PointCloud(points=tuple(points))