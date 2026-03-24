"""ThrottledExecutor — wraps a callable with automatic throttling + retries."""

from typing import Any, Callable

from .throttle import Throttle
from .config import ThrottleConfig


class RateLimitError(Exception):
    """Raise this inside a wrapped function to signal a 429/rate-limit event.

    ThrottledExecutor catches it, calls throttle.rate_limited(), and retries.
    """


class ThrottledExecutor:
    """Wraps any callable with adaptive throttling and automatic retries.

    Usage::

        def call_openai(prompt: str) -> str:
            response = openai.chat.completions.create(...)
            return response.choices[0].message.content

        executor = ThrottledExecutor(call_openai, max_retries=5)
        result = executor("Hello, world!")

    If the wrapped function raises :class:`RateLimitError`, the executor:
    1. Signals ``throttle.rate_limited()``
    2. Calls ``throttle.wait()``
    3. Retries up to *max_retries* times

    On success it calls ``throttle.success()``.
    On other exceptions it calls ``throttle.error()`` and re-raises after
    exhausting retries.
    """

    def __init__(
        self,
        func: Callable[..., Any],
        throttle: Throttle | None = None,
        max_retries: int = 3,
    ) -> None:
        self._func = func
        self._throttle = throttle or Throttle()
        self._max_retries = max_retries

    # ------------------------------------------------------------------
    # Callable interface
    # ------------------------------------------------------------------

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        last_exc: Exception | None = None

        for attempt in range(self._max_retries + 1):
            self._throttle.wait()
            try:
                result = self._func(*args, **kwargs)
                self._throttle.success()
                return result
            except RateLimitError as exc:
                last_exc = exc
                self._throttle.rate_limited()
                # On last attempt, fall through and raise
                if attempt == self._max_retries:
                    raise
            except Exception as exc:
                last_exc = exc
                self._throttle.error()
                raise

        # Should not reach here, but satisfy type checkers
        raise RuntimeError("Unreachable") from last_exc  # pragma: no cover

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    @property
    def throttle(self) -> Throttle:
        """The underlying Throttle instance."""
        return self._throttle
