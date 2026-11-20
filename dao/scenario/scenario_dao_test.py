"""Tests for scenario YAML loading."""

from pathlib import Path

from dao.scenario.scenario_dao import ScenarioDao


def test_load_square_scenario() -> None:
    path = Path(__file__).resolve().parents[2] / "scenarios" / "square_5m.yaml"
    scenario = ScenarioDao().load(path)
    assert scenario.name == "square_5m"
    assert scenario.goal.side_m == 5.0
    assert scenario.pass_criteria.waypoint_tolerance_m == 1.0