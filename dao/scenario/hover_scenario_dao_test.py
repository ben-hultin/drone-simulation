"""Tests for hover scenario YAML loading."""

from pathlib import Path

from dao.scenario.hover_scenario_dao import HoverScenarioDao


def test_load_hover_scenario() -> None:
    root = Path(__file__).resolve().parents[2]
    scenario = HoverScenarioDao().load(root / "scenarios" / "hover_5m_depth.yaml")
    assert scenario.name == "hover_5m_depth"
    assert scenario.model == "gz_x500_depth"
    assert scenario.hover.altitude_m == 5.0
    assert scenario.pass_criteria.require_depth_frame is True