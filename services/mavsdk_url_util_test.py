"""Tests for MAVSDK URL validation."""

import pytest

from services.mavsdk_url_util import validate_connection_url


def test_loopback_url_allowed() -> None:
    assert validate_connection_url("udpin://127.0.0.1:14540") == "udpin://127.0.0.1:14540"


def test_wildcard_bind_rejected() -> None:
    with pytest.raises(ValueError, match="wildcard_bind"):
        validate_connection_url("udpin://0.0.0.0:14540")


def test_remote_host_rejected() -> None:
    with pytest.raises(ValueError, match="remote_host"):
        validate_connection_url("udpin://192.168.1.10:14540")