"""ThrottleConfig — configuration for adaptive throttling."""

from dataclasses import dataclass, field


@dataclass
class ThrottleConfig:
    """Configuration for Throttle controller.

    Args:
        min_delay_ms: Minimum delay between calls in milliseconds.
        max_delay_ms: Maximum delay (cap) in milliseconds.
        backoff_factor: Multiplier applied on rate-limit signal.
        jitter_ms: Random jitter range added to avoid thundering herd.
    """

    min_delay_ms: float = 0.0
    max_delay_ms: float = 60_000.0
    backoff_factor: float = 2.0
    jitter_ms: float = 100.0
    initial_delay_ms: float = field(default=100.0)

    def __post_init__(self) -> None:
        if self.min_delay_ms < 0:
            raise ValueError("min_delay_ms must be >= 0")
        if self.max_delay_ms < self.min_delay_ms:
            raise ValueError("max_delay_ms must be >= min_delay_ms")
        if self.backoff_factor < 1.0:
            raise ValueError("backoff_factor must be >= 1.0")
        if self.jitter_ms < 0:
            raise ValueError("jitter_ms must be >= 0")
        if self.initial_delay_ms < 0:
            raise ValueError("initial_delay_ms must be >= 0")
