"""Tests for live MAVSDK factory."""

from services.mavsdk_live_util import create_live_gateway


def test_create_live_gateway_validates_url() -> None:
    gateway = create_live_gateway("udpin://127.0.0.1:14540")
    assert gateway is not None