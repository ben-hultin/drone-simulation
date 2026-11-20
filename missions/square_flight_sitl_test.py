"""Optional live SITL square smoke (opt-in via RUN_LIVE_SITL=1)."""

import os

import pytest


@pytest.mark.skipif(os.environ.get("RUN_LIVE_SITL") != "1", reason="live_sitl_opt_in")
def test_square_live_placeholder(sitl_stack) -> None:
    """Uses sitl_stack so Phase 1 fixture is wired when RUN_LIVE_SITL=1."""
    assert sitl_stack.can_launch