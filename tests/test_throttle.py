"""Tests for Throttle adaptive controller."""

import pytest
from unittest.mock import patch, MagicMock
from agent_throttle import Throttle, ThrottleConfig


@pytest.fixture
def throttle():
    cfg = ThrottleConfig(
        min_delay_ms=0,
        max_delay_ms=10_000,
        backoff_factor=2.0,
        jitter_ms=0,  # zero jitter for deterministic tests
        initial_delay_ms=100,
    )
    return Throttle(cfg)


class TestThrottleWait:
    def test_wait_calls_sleep(self, throttle):
        with patch("time.sleep") as mock_sleep:
            throttle.wait()
            mock_sleep.assert_called_once_with(pytest.approx(0.1, abs=1e-6))

    def test_wait_increments_total_calls(self, throttle):
        with patch("time.sleep"):
            throttle.wait()
            throttle.wait()
        assert throttle.stats()["total_calls"] == 2

    def test_wait_zero_delay_no_sleep(self):
        cfg = ThrottleConfig(min_delay_ms=0, max_delay_ms=1000, jitter_ms=0, initial_delay_ms=0)
        t = Throttle(cfg)
        with patch("time.sleep") as mock_sleep:
            t.wait()
            mock_sleep.assert_not_called()


class TestThrottleSuccess:
    def test_success_reduces_delay_from_throttled(self, throttle):
        throttle.rate_limited()
        high = throttle.current_delay_ms
        throttle.success()
        assert throttle.current_delay_ms < high

    def test_success_transitions_to_recovering(self, throttle):
        throttle.rate_limited()
        throttle.success()
        assert throttle.state in ("recovering", "normal")

    def test_repeated_success_returns_to_normal(self, throttle):
        throttle.rate_limited()
        for _ in range(20):
            throttle.success()
        assert throttle.state == "normal"

    def test_success_increments_counter(self, throttle):
        with patch("time.sleep"):
            throttle.wait()
        throttle.success()
        assert throttle.stats()["success_count"] == 1


class TestThrottleRateLimited:
    def test_rate_limited_increases_delay(self, throttle):
        initial = throttle.current_delay_ms
        throttle.rate_limited()
        assert throttle.current_delay_ms > initial

    def test_rate_limited_sets_throttled_state(self, throttle):
        throttle.rate_limited()
        assert throttle.state == "throttled"

    def test_rate_limited_capped_at_max(self):
        cfg = ThrottleConfig(max_delay_ms=200, jitter_ms=0, initial_delay_ms=100)
        t = Throttle(cfg)
        for _ in range(10):
            t.rate_limited()
        assert t.current_delay_ms <= 200

    def test_rate_limited_increments_counter(self, throttle):
        throttle.rate_limited()
        throttle.rate_limited()
        assert throttle.stats()["rate_limited_count"] == 2


class TestThrottleError:
    def test_error_increases_delay(self, throttle):
        initial = throttle.current_delay_ms
        with patch("random.uniform", return_value=0):
            throttle.error()
        assert throttle.current_delay_ms > initial

    def test_error_increments_counter(self, throttle):
        throttle.error()
        assert throttle.stats()["error_count"] == 1

    def test_error_does_not_exceed_max(self):
        cfg = ThrottleConfig(max_delay_ms=150, jitter_ms=0, initial_delay_ms=100)
        t = Throttle(cfg)
        for _ in range(20):
            with patch("random.uniform", return_value=0):
                t.error()
        assert t.current_delay_ms <= 150


class TestThrottleStats:
    def test_stats_keys(self, throttle):
        s = throttle.stats()
        assert set(s.keys()) == {
            "state", "current_delay_ms", "total_calls",
            "success_count", "rate_limited_count", "error_count",
        }

    def test_stats_initial_state(self, throttle):
        s = throttle.stats()
        assert s["state"] == "normal"
        assert s["total_calls"] == 0

    def test_default_config(self):
        t = Throttle()
        assert t.current_delay_ms == 100.0
        assert t.state == "normal"
