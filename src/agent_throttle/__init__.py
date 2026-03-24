"""agent-throttle: Adaptive throttling for LLM API calls."""

from .config import ThrottleConfig
from .throttle import Throttle
from .executor import ThrottledExecutor, RateLimitError
from .adaptive import AdaptiveThrottle

__all__ = [
    "ThrottleConfig",
    "Throttle",
    "ThrottledExecutor",
    "RateLimitError",
    "AdaptiveThrottle",
]

__version__ = "1.0.0"
