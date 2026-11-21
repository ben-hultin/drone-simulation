"""Load hover scenarios from YAML."""

from pathlib import Path

import yaml

from dao.scenario.hover_scenario_types import (
    HoverConfig,
    HoverPassCriteria,
    HoverScenario,
    HoverSpawn,
    PerceptionLimits,
)


class HoverScenarioDao:
    def load(self, path: Path) -> HoverScenario:
        resolved = _resolve_scenario_path(path)
        raw = yaml.safe_load(resolved.read_text(encoding="utf-8"))
        return _parse_scenario(raw)


def _resolve_scenario_path(path: Path) -> Path:
    resolved = path.resolve()
    scenarios_root = Path(__file__).resolve().parents[2] / "scenarios"
    if not resolved.is_relative_to(scenarios_root.resolve()):
        raise ValueError("scenario_path_outside_scenarios_dir")
    return resolved


def _parse_scenario(raw: dict) -> HoverScenario:
    spawn = raw["spawn"]
    hover = raw["hover"]
    criteria = raw["pass_criteria"]
    perception = raw.get("perception", {})
    return HoverScenario(
        name=str(raw["name"]),
        world=str(raw["world"]),
        model=str(raw.get("model", "gz_x500_depth")),
        spawn=HoverSpawn(
            north_m=float(spawn["north_m"]),
            east_m=float(spawn["east_m"]),
            alt_m=float(spawn["alt_m"]),
        ),
        hover=HoverConfig(
            altitude_m=float(hover["altitude_m"]),
            duration_s=float(hover["duration_s"]),
            position_tolerance_m=float(hover["position_tolerance_m"]),
        ),
        time_limit_s=float(raw["time_limit_s"]),
        pass_criteria=HoverPassCriteria(
            require_disarmed=bool(criteria.get("require_disarmed", True)),
            require_no_failsafe=bool(criteria.get("require_no_failsafe", True)),
            require_pose=bool(criteria.get("require_pose", True)),
            require_depth_frame=bool(criteria.get("require_depth_frame", True)),
        ),
        perception=PerceptionLimits(
            max_pose_age_s=float(perception.get("max_pose_age_s", 1.0)),
            max_depth_age_s=float(perception.get("max_depth_age_s", 1.0)),
        ),
    )