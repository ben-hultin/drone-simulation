# Phase 2 — ROS 2 integration and perception

Exit: `OffboardHoverMission` reads pose and depth, converts depth to a point cloud, publishes offboard hold setpoints, hovers, lands, and records rosbag metadata next to the PX4 ULog copy.

## SITL model

Use `make px4_sitl gz_x500_depth` from your PX4-Autopilot clone. `SitlLauncherService` accepts `target="gz_x500_depth"`.

## ROS 2 workspace

Launch and bridge YAML live under `ros2_ws/src/drone_autonomy/`. Mission logic stays in `missions/`; ROS nodes only bridge topics per `config/ros_gz_bridge.yaml`.

Run Micro XRCE-DDS Agent and `px4_msgs` per PX4 ROS 2 user guide before echoing `/fmu/out/vehicle_odometry`.

## Python entry

```python
from dao.scenario.hover_scenario_dao import HoverScenarioDao
from missions.offboard_hover import OffboardHoverMission
```

Wire real `PoseSource`, `DepthSource`, and `OffboardPublisher` implementations in `services/` when ROS is available.

## Verify (no simulator)

```bash
./harness-loop.sh
pytest missions/offboard_hover_test.py
```