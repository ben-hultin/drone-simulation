# Autonomous Drone Simulation – Phased Development Plan

Nov 15, 2026 · @Ben

## Overview

Build a free, local simulation stack that flies an autonomous drone through a library of scenarios and scores each run automatically. Seven phases over roughly 14–20 weeks for one engineer; every phase ends with an automated pass/fail test, not a demo.

- **Goal:** an autonomous quadcopter that plans and flies collision-free through varied scenarios, verified by a repeatable test suite.
- **Stack:** PX4 SITL (flight control), Gazebo Harmonic (world and sensors), ROS 2 Jazzy (autonomy), MAVSDK-Python + pytest (test harness), Blender (assets). All free.
- **Dev machine:** MacBook Air M3, 16 GB. Fine for one drone in one scenario; heavy batch runs move to a Linux CI runner.
- **Principles:** one scenario end to end before breadth; every scenario is code (world file + mission + pass criteria); metrics tracked from the first test onward.

## Phase 0 — Environment setup (1 week)

Exit when `make px4_sitl gz_x500` flies on the Mac and QGroundControl connects to it.

- [ ] Install Xcode CLI tools, Homebrew, raise the open-file limit
- [ ] Clone PX4-Autopilot; run `./Tools/setup/macos.sh --sim-tools` (Gazebo Harmonic + XQuartz)
- [ ] Install QGroundControl; arm, take off and land by hand
- [ ] Install MAVSDK-Python and pytest in a project virtualenv
- [ ] Create the project repo: `worlds/`, `models/`, `missions/`, `tests/`, `ros2_ws/`, `docs/`
- [ ] Fallback if the native build fights you: Ubuntu 24.04 ARM VM in UTM, or a used Linux PC

## Phase 1 — Scripted flight and first automated test (1–2 weeks)

Exit when `pytest` launches SITL headless, flies a waypoint mission and passes or fails on its own.

- [ ] MAVSDK script: connect, arm, take off to 5 m, fly a square, land
- [ ] pytest fixture that starts and stops PX4 SITL + Gazebo headless per test
- [ ] Assertions: reached each waypoint within 1 m, landed, disarmed, no failsafe
- [ ] Save the `.ulg` log per run; parse it with pyulog for flight time and max position error
- [ ] First scenario file format: world, spawn pose, goal, time limit, pass criteria (YAML)

## Phase 2 — ROS 2 integration and perception (2–3 weeks)

Exit when a ROS 2 node reads the drone's pose and depth camera and can take off and hover the drone through offboard mode.

- [ ] Install ROS 2 Jazzy (RoboStack natively, or the UTM VM) and the Micro XRCE-DDS Agent
- [ ] Build `px4_msgs`; echo `/fmu/out/vehicle_odometry` from SITL
- [ ] Switch to the `gz_x500_depth` model; bridge camera and depth topics with `ros_gz_bridge`
- [ ] Offboard control node: publish `OffboardControlMode` + `TrajectorySetpoint`, arm, hover, land
- [ ] Depth image → point cloud node; view it live in Foxglove or RViz
- [ ] Record a rosbag per run alongside the PX4 log

## Phase 3 — Autonomous navigation (4–6 weeks)

Exit when the drone flies from start to goal around a static wall it has never seen, with no human input, in an automated test.

- [ ] Mapping: point cloud → occupancy map (OctoMap or a simple voxel grid)
- [ ] Global planner: A\* or RRT\* on the map toward the goal
- [ ] Local avoidance: replan or reactive avoidance when new obstacles appear
- [ ] Trajectory follower: smooth setpoints to PX4, speed and climb limits
- [ ] Mission state machine: takeoff → navigate → land, with abort on timeout or stuck
- [ ] Study `px4-ros2-drone-nav` (ROS 2 Jazzy + PX4 + Gazebo) for architecture; its CUDA optimizer will not run on the Mac
- [ ] First autonomous test: single wall between start and goal

## Phase 4 — Scenario library and test harness (2–3 weeks)

Exit when one command runs every scenario headless and prints a scorecard. Each scenario = a Gazebo world + spawn/goal + pass criteria in YAML.

| Scenario | What it tests | Pass criteria |
| --- | --- | --- |
| Single wall | Basic detect-and-avoid | Reaches goal, zero collisions |
| Forest | Dense static obstacles | Reaches goal, min clearance ≥ 0.5 m |
| Urban canyon | Buildings, narrow streets | Reaches goal within time limit |
| Narrow gap | Precise path through an opening | Passes gap without contact |
| Moving obstacle | Dynamic replanning | No collision with the mover |
| Wind gusts | Control under disturbance | Path error within bound |
| Precision landing | Final approach accuracy | Lands within 0.5 m of target |

Metrics logged per run: success, collisions, minimum clearance, time to goal, path length vs. straight line. Thresholds above are starting points to tune.

- [ ] Scenario runner: pytest parametrized over `scenarios/*.yaml`
- [ ] Collision detection from Gazebo contact sensors
- [ ] Metrics written to CSV/JSON per run; summary table at the end

## Phase 5 — Fault injection and robustness (2 weeks)

Exit when every scenario also runs with injected faults and the drone either completes the mission or fails safe (hover, return home, or land) every time.

- [ ] Enable PX4 failure injection (`SYS_FAILURE_EN`) and script the `failure` command mid-flight
- [ ] Faults: GPS loss, depth camera dropout, IMU noise, low battery, single-motor loss
- [ ] Expected behavior per fault written into the scenario YAML (continue, RTL, land)
- [ ] Sensor noise and latency sweeps to find where autonomy breaks
- [ ] Geofence breach and lost-link tests

## Phase 6 — CI, scale-out and path to hardware (2–3 weeks, then ongoing)

Exit when every commit runs the full scenario suite on a Linux runner and posts the scorecard, and one scenario has been reproduced on a real airframe.

- [ ] Dockerize SITL + Gazebo + ROS 2 for headless Linux runs
- [ ] GitHub Actions (or a self-hosted Linux box) runs the suite per commit; fail on metric regressions
- [ ] Trend dashboard of success rate and clearance over time
- [ ] Randomized scenario variants (obstacle positions, wind, start pose) for coverage
- [ ] Hardware-in-the-loop with a Pixhawk-class flight controller
- [ ] First real-world test flight of the single-wall scenario, tethered or in a net

## Timeline and risks

About 14–20 weeks end to end for one engineer; estimates assume part of the setup goes smoothly on macOS.

&#91;embedded content: roadmap · 7 phases, 7 test gates\]

Phase 3 carries the most uncertainty; Phases 4–5 can start in parallel once one autonomous test passes.

| Risk | Impact | Mitigation |
| --- | --- | --- |
| PX4/Gazebo native build breaks on macOS | Phase 0 slips | Ubuntu ARM VM in UTM, or a used Linux PC |
| Fanless Air throttles on long runs | Slow, flaky tests | Run headless; batch suites on Linux CI |
| ROS 2 ↔ Gazebo friction on macOS | Phase 2 slips | RoboStack natively; else move fully to Linux |
| Planner tuning runs long | Phase 3 overruns | Start with simple reactive avoidance; reuse reference-repo design |
| Sim-to-real gap | Passes in sim, fails in the air | Noise, wind and randomized variants; HIL before real flight |
