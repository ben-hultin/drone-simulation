"""Convert bridged depth frames into point clouds for perception nodes."""

from missions.depth_to_pointcloud_util import depth_frame_to_point_cloud
from services.perception_protocol import DepthFrame, PointCloud


class DepthToPointCloudConverter:
    def convert(self, frame: DepthFrame) -> PointCloud:
        return depth_frame_to_point_cloud(frame)