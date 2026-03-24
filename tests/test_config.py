"""Tests for ThrottleConfig."""

import pytest
from agent_throttle import ThrottleConfig


class TestThrottleConfigDefaults:
    def test_default_values(self):
        cfg = ThrottleConfig()
        assert cfg.min_delay_ms == 0.0
        assert cfg.max_delay_ms == 60_000.0
        assert cfg.backoff_factor == 2.0
        assert cfg.jitter_ms == 100.0
        assert cfg.initial_delay_ms == 100.0

    def test_custom_values(self):
        cfg = ThrottleConfig(min_delay_ms=50, max_delay_ms=5000, backoff_factor=3.0, jitter_ms=50)
        assert cfg.min_delay_ms == 50
        assert cfg.max_delay_ms == 5000
        assert cfg.backoff_factor == 3.0
        assert cfg.jitter_ms == 50

    def test_invalid_min_delay(self):
        with pytest.raises(ValueError, match="min_delay_ms"):
            ThrottleConfig(min_delay_ms=-1)

    def test_invalid_max_less_than_min(self):
        with pytest.raises(ValueError, match="max_delay_ms"):
            ThrottleConfig(min_delay_ms=100, max_delay_ms=50)

    def test_invalid_backoff_factor(self):
        with pytest.raises(ValueError, match="backoff_factor"):
            ThrottleConfig(backoff_factor=0.5)

    def test_invalid_jitter(self):
        with pytest.raises(ValueError, match="jitter_ms"):
            ThrottleConfig(jitter_ms=-10)
