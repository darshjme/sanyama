"""Throttle — adaptive throttle controller."""

import random
import time
from typing import Any

from .config import ThrottleConfig


class Throttle:
    """Adaptive throttle controller for LLM API calls.

    Tracks call outcomes and adjusts pacing automatically:
    - success() → gradually reduces delay (recovery)
    - rate_limited() → exponential backoff
    - error() → mild increase

    States:
        normal    — delay at or below initial_delay_ms
        throttled — delay increased due to rate limit
        recovering — delay decreasing back toward normal
    """

    _RECOVERY_FACTOR = 0.8  # reduce delay by 20% on each success

    def __init__(self, config: ThrottleConfig | None = None) -> None:
        self._config = config or ThrottleConfig()
        self._current_delay_ms: float = self._config.initial_delay_ms
        self._state: str = "normal"
        self._total_calls: int = 0
        self._rate_limited_count: int = 0
        self._error_count: int = 0
        self._success_count: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def wait(self) -> None:
        """Sleep for the current delay before issuing an API call."""
        delay_s = self._current_delay_ms / 1000.0
        if delay_s > 0:
            time.sleep(delay_s)
        self._total_calls += 1

    def success(self) -> None:
        """Signal a successful API call; reduces delay toward minimum."""
        self._success_count += 1
        if self._state in ("throttled", "recovering"):
            self._state = "recovering"
            self._current_delay_ms = max(
                self._config.min_delay_ms,
                self._current_delay_ms * self._RECOVERY_FACTOR,
            )
            if self._current_delay_ms <= self._config.initial_delay_ms:
                self._state = "normal"
                self._current_delay_ms = self._config.initial_delay_ms
        else:
            # already normal — gently floor at min
            self._current_delay_ms = max(
                self._config.min_delay_ms,
                self._current_delay_ms * self._RECOVERY_FACTOR,
            )

    def rate_limited(self) -> None:
        """Signal a 429/rate-limit response; applies exponential backoff."""
        self._rate_limited_count += 1
        self._state = "throttled"
        jitter = random.uniform(0, self._config.jitter_ms)
        new_delay = self._current_delay_ms * self._config.backoff_factor + jitter
        self._current_delay_ms = min(new_delay, self._config.max_delay_ms)

    def error(self) -> None:
        """Signal a generic (non-rate-limit) error; mild delay increase."""
        self._error_count += 1
        jitter = random.uniform(0, self._config.jitter_ms / 2)
        new_delay = self._current_delay_ms * 1.2 + jitter
        self._current_delay_ms = min(new_delay, self._config.max_delay_ms)
        if self._state == "normal":
            self._state = "recovering"

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_delay_ms(self) -> float:
        """Current wait delay in milliseconds."""
        return self._current_delay_ms

    @property
    def state(self) -> str:
        """One of: 'normal', 'throttled', 'recovering'."""
        return self._state

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """Return a snapshot of throttle statistics."""
        return {
            "state": self._state,
            "current_delay_ms": round(self._current_delay_ms, 3),
            "total_calls": self._total_calls,
            "success_count": self._success_count,
            "rate_limited_count": self._rate_limited_count,
            "error_count": self._error_count,
        }
