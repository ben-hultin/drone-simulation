"""Tests for square flight scenario helpers."""

from pathlib import Path

import pytest

from dao.scenario.scenario_dao import ScenarioDao
from missions.square_flight_util import waypoints_for_scenario


def test_waypoints_for_square_scenario() -> None:
    path = Path(__file__).resolve().parents[1] / "scenarios" / "square_5m.yaml"
    scenario = ScenarioDao().load(path)
    points = waypoints_for_scenario(scenario)
    assert len(points) == 4
    assert points[0][0] == 5.0


def test_spawn_offsets_waypoints() -> None:
    path = Path(__file__).resolve().parents[1] / "scenarios" / "square_5m.yaml"
    scenario = ScenarioDao().load(path)
    spawn_scenario = scenario.__class__(
        name=scenario.name,
        world=scenario.world,
        spawn=scenario.spawn.__class__(north_m=2.0, east_m=3.0, alt_m=0.0),
        goal=scenario.goal,
        time_limit_s=scenario.time_limit_s,
        pass_criteria=scenario.pass_criteria,
    )
    first = waypoints_for_scenario(spawn_scenario)[0]
    assert first == (7.0, 3.0, 5.0)


def test_unsupported_pattern_raises() -> None:
    path = Path(__file__).resolve().parents[1] / "scenarios" / "square_5m.yaml"
    scenario = ScenarioDao().load(path)
    circle_goal = scenario.goal.__class__(pattern="circle", side_m=1, altitude_m=1)
    bad = scenario.__class__(**{**scenario.__dict__, "goal": circle_goal})
    with pytest.raises(ValueError, match="unsupported_goal_pattern"):
        waypoints_for_scenario(bad)