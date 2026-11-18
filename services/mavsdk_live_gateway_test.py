"""Tests for live MAVSDK gateway error paths."""

import asyncio

import pytest

from services.mavsdk_live_gateway import MavsdkLiveGateway


def test_health_requires_connection() -> None:
    gateway = MavsdkLiveGateway("udpin://127.0.0.1:14540")
    with pytest.raises(RuntimeError, match="mavsdk_not_connected"):
        asyncio.run(gateway.get_health())


def test_gateway_rejects_wildcard_url() -> None:
    with pytest.raises(ValueError, match="wildcard"):
        MavsdkLiveGateway("udpin://0.0.0.0:14540")