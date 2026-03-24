# Changelog

All notable changes to `agent-throttle` are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

---

## [1.0.0] — 2026-03-24

### Added
- `ThrottleConfig` — dataclass with validation for all throttle parameters
- `Throttle` — adaptive controller with `wait()`, `success()`, `rate_limited()`, `error()`, `stats()`
- `ThrottledExecutor` — callable wrapper with automatic retry on `RateLimitError`
- `RateLimitError` — exception class for signalling 429-style rate limits
- `AdaptiveThrottle` — latency-based delay suggestion with sliding window average
- 47 pytest tests with full `time.sleep` / `time.time` mocking
- Zero dependencies (Python stdlib only)
- Python 3.10+ support
