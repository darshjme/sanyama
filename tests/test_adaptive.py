"""Tests for AdaptiveThrottle."""

import pytest
from agent_throttle import AdaptiveThrottle


class TestAdaptiveThrottleInit:
    def test_default_values(self):
        at = AdaptiveThrottle()
        assert at.avg_latency_ms == 0.0
        assert at.suggested_delay_ms == 0.0

    def test_invalid_target(self):
        with pytest.raises(ValueError, match="target_latency_ms"):
            AdaptiveThrottle(target_latency_ms=0)

    def test_invalid_window(self):
        with pytest.raises(ValueError, match="window"):
            AdaptiveThrottle(window=0)


class TestAdaptiveThrottleRecord:
    def test_record_single_sample(self):
        at = AdaptiveThrottle(target_latency_ms=500)
        at.record(300)
        assert at.avg_latency_ms == pytest.approx(300)

    def test_avg_multiple_samples(self):
        at = AdaptiveThrottle(target_latency_ms=500, window=3)
        at.record(100)
        at.record(200)
        at.record(300)
        assert at.avg_latency_ms == pytest.approx(200)

    def test_window_slides(self):
        at = AdaptiveThrottle(target_latency_ms=500, window=2)
        at.record(100)
        at.record(200)
        at.record(900)  # pushes out 100
        assert at.avg_latency_ms == pytest.approx(550)

    def test_invalid_latency(self):
        at = AdaptiveThrottle()
        with pytest.raises(ValueError, match="latency_ms"):
            at.record(-1)


class TestAdaptiveThrottleSuggestedDelay:
    def test_no_delay_when_under_target(self):
        at = AdaptiveThrottle(target_latency_ms=500)
        at.record(400)
        assert at.suggested_delay_ms == 0.0

    def test_no_delay_when_at_target(self):
        at = AdaptiveThrottle(target_latency_ms=500)
        at.record(500)
        assert at.suggested_delay_ms == 0.0

    def test_positive_delay_when_over_target(self):
        at = AdaptiveThrottle(target_latency_ms=500)
        at.record(1000)  # 2x target
        assert at.suggested_delay_ms > 0

    def test_delay_scales_with_overrun(self):
        at = AdaptiveThrottle(target_latency_ms=500)
        at.record(1000)  # overrun by 500ms (100% over)
        # overrun_ratio = (1000-500)/500 = 1.0 → delay = 500 * 1.0 = 500
        assert at.suggested_delay_ms == pytest.approx(500.0)

    def test_no_samples_returns_zero(self):
        at = AdaptiveThrottle()
        assert at.suggested_delay_ms == 0.0
