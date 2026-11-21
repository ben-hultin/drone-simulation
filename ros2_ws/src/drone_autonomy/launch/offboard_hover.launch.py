"""Launch ros_gz_bridge and document offboard hover params (nodes stay in missions/)."""

from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument


def generate_launch_description() -> LaunchDescription:
    pkg_root = Path(__file__).resolve().parents[1]
    bridge_config = str(pkg_root / "config" / "ros_gz_bridge.yaml")
    params_config = str(pkg_root / "config" / "offboard_hover_params.yaml")
    return LaunchDescription(
        [
            DeclareLaunchArgument("bridge_config", default_value=bridge_config),
            DeclareLaunchArgument("mission_params", default_value=params_config),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument(
                "ros_gz_bridge_cmd",
                default_value=(
                    "ros2 run ros_gz_bridge parameter_bridge "
                    f"--ros-args -p config_file:={bridge_config}"
                ),
            ),
            DeclareLaunchArgument(
                "mission_note",
                default_value=(
                    "Run OffboardHoverMission from missions/offboard_hover.py with "
                    f"params at {params_config}"
                ),
            ),
        ]
    )