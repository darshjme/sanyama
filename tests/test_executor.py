"""Tests for ThrottledExecutor and RateLimitError."""

import pytest
from unittest.mock import patch, MagicMock, call
from agent_throttle import ThrottledExecutor, RateLimitError, Throttle, ThrottleConfig


@pytest.fixture
def fast_throttle():
    cfg = ThrottleConfig(min_delay_ms=0, max_delay_ms=1000, jitter_ms=0, initial_delay_ms=0)
    return Throttle(cfg)


class TestRateLimitError:
    def test_is_exception(self):
        err = RateLimitError("too many requests")
        assert isinstance(err, Exception)

    def test_message(self):
        err = RateLimitError("429")
        assert "429" in str(err)


class TestThrottledExecutorSuccess:
    def test_calls_function(self, fast_throttle):
        func = MagicMock(return_value="hello")
        executor = ThrottledExecutor(func, throttle=fast_throttle)
        with patch("time.sleep"):
            result = executor("arg1", key="val")
        func.assert_called_once_with("arg1", key="val")
        assert result == "hello"

    def test_returns_function_result(self, fast_throttle):
        executor = ThrottledExecutor(lambda x: x * 2, throttle=fast_throttle)
        with patch("time.sleep"):
            assert executor(5) == 10

    def test_success_recorded_on_throttle(self, fast_throttle):
        executor = ThrottledExecutor(lambda: None, throttle=fast_throttle)
        with patch("time.sleep"):
            executor()
        assert fast_throttle.stats()["success_count"] == 1


class TestThrottledExecutorRetries:
    def test_retries_on_rate_limit_error(self, fast_throttle):
        attempts = {"n": 0}
        def flaky():
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise RateLimitError("429")
            return "ok"

        executor = ThrottledExecutor(flaky, throttle=fast_throttle, max_retries=5)
        with patch("time.sleep"):
            result = executor()
        assert result == "ok"
        assert attempts["n"] == 3

    def test_raises_after_max_retries(self, fast_throttle):
        func = MagicMock(side_effect=RateLimitError("always rate limited"))
        executor = ThrottledExecutor(func, throttle=fast_throttle, max_retries=2)
        with patch("time.sleep"), pytest.raises(RateLimitError):
            executor()
        assert func.call_count == 3  # initial + 2 retries

    def test_rate_limited_count_increments(self, fast_throttle):
        func = MagicMock(side_effect=RateLimitError("429"))
        executor = ThrottledExecutor(func, throttle=fast_throttle, max_retries=2)
        with patch("time.sleep"), pytest.raises(RateLimitError):
            executor()
        assert fast_throttle.stats()["rate_limited_count"] == 3

    def test_generic_error_not_retried(self, fast_throttle):
        func = MagicMock(side_effect=ValueError("bad input"))
        executor = ThrottledExecutor(func, throttle=fast_throttle, max_retries=3)
        with patch("time.sleep"), pytest.raises(ValueError):
            executor()
        assert func.call_count == 1

    def test_error_recorded_on_generic_exception(self, fast_throttle):
        func = MagicMock(side_effect=RuntimeError("oops"))
        executor = ThrottledExecutor(func, throttle=fast_throttle, max_retries=3)
        with patch("time.sleep"), pytest.raises(RuntimeError):
            executor()
        assert fast_throttle.stats()["error_count"] == 1


class TestThrottledExecutorThrottleProperty:
    def test_throttle_property(self, fast_throttle):
        executor = ThrottledExecutor(lambda: None, throttle=fast_throttle)
        assert executor.throttle is fast_throttle

    def test_default_throttle_created(self):
        executor = ThrottledExecutor(lambda: None)
        assert isinstance(executor.throttle, Throttle)
