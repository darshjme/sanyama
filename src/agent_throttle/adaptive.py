"""AdaptiveThrottle — learns optimal delay from observed response latencies."""

from collections import deque


class AdaptiveThrottle:
    """Monitors API response latencies and suggests a throttle delay.

    If the rolling-average latency exceeds *target_latency_ms*, it returns a
    positive suggested delay proportional to the overrun.  If latency is
    below target, it returns 0 (no artificial delay needed).

    Typical usage alongside :class:`Throttle`::

        adaptive = AdaptiveThrottle(target_latency_ms=500)
        throttle  = Throttle()

        import time
        t0 = time.monotonic()
        result = api_call()
        latency_ms = (time.monotonic() - t0) * 1000

        adaptive.record(latency_ms)
        # Optionally push adaptive hint into throttle
        if adaptive.suggested_delay_ms > throttle.current_delay_ms:
            throttle.rate_limited()
    """

    def __init__(self, target_latency_ms: float = 500.0, window: int = 10) -> None:
        if target_latency_ms <= 0:
            raise ValueError("target_latency_ms must be > 0")
        if window < 1:
            raise ValueError("window must be >= 1")

        self._target = target_latency_ms
        self._window = window
        self._samples: deque[float] = deque(maxlen=window)

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(self, latency_ms: float) -> None:
        """Record an observed API latency in milliseconds."""
        if latency_ms < 0:
            raise ValueError("latency_ms must be >= 0")
        self._samples.append(latency_ms)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def avg_latency_ms(self) -> float:
        """Rolling average latency over the last *window* samples."""
        if not self._samples:
            return 0.0
        return sum(self._samples) / len(self._samples)

    @property
    def suggested_delay_ms(self) -> float:
        """Suggested pre-call delay in milliseconds.

        Returns 0.0 when average latency is within target.
        Scales linearly with overrun beyond target.
        """
        avg = self.avg_latency_ms
        if avg <= self._target:
            return 0.0
        # Delay proportional to how much latency exceeds target
        overrun_ratio = (avg - self._target) / self._target
        return self._target * overrun_ratio  # symmetric scaling
