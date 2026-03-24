# agent-throttle

**Adaptive throttling for LLM API calls.**

Dumb fixed delays waste throughput. `agent-throttle` detects rate-limit signals (HTTP 429s, slow responses) and adjusts call pacing automatically — backing off when needed, speeding up when safe.

```
pip install agent-throttle
```

Zero dependencies. Python ≥ 3.10.

---

## Quick Start

### Basic adaptive throttling

```python
import openai
from agent_throttle import Throttle, ThrottledExecutor, RateLimitError

client = openai.OpenAI()

def call_gpt(prompt: str) -> str:
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content
    except openai.RateLimitError:
        raise RateLimitError("OpenAI 429")  # signal the executor

# Wrap with throttling + auto-retry
executor = ThrottledExecutor(call_gpt, max_retries=5)

# Use exactly like the original function
answer = executor("What is the capital of France?")
print(answer)  # Paris
```

On every `RateLimitError` the executor signals `throttle.rate_limited()`, waits the (exponentially increasing) delay, then retries — up to `max_retries` times.

---

### Adaptive delay based on response latency

```python
import time
from agent_throttle import AdaptiveThrottle, Throttle

throttle  = Throttle()
adaptive  = AdaptiveThrottle(target_latency_ms=500, window=10)

def api_call(prompt: str) -> str:
    throttle.wait()          # wait current delay
    t0 = time.monotonic()
    result = expensive_llm_call(prompt)
    latency_ms = (time.monotonic() - t0) * 1000

    adaptive.record(latency_ms)
    throttle.success()

    # If API is getting slow, pre-emptively back off
    if adaptive.suggested_delay_ms > throttle.current_delay_ms:
        throttle.rate_limited()

    return result
```

---

### Manual control

```python
from agent_throttle import Throttle, ThrottleConfig

cfg = ThrottleConfig(
    min_delay_ms=0,
    max_delay_ms=30_000,
    backoff_factor=2.0,   # double delay on each 429
    jitter_ms=200,        # ±200ms random jitter
)
throttle = Throttle(cfg)

for prompt in prompts:
    throttle.wait()
    try:
        result = call_llm(prompt)
        throttle.success()           # delay shrinks
    except RateLimitHTTPError:
        throttle.rate_limited()      # delay doubles
    except Exception:
        throttle.error()             # delay grows mildly
        raise

print(throttle.stats())
# {'state': 'recovering', 'current_delay_ms': 400.0,
#  'total_calls': 50, 'success_count': 47,
#  'rate_limited_count': 2, 'error_count': 1}
```

---

## API Reference

### `ThrottleConfig`

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_delay_ms` | `0` | Floor delay (ms) |
| `max_delay_ms` | `60000` | Ceiling delay (ms) |
| `backoff_factor` | `2.0` | Multiplier on `rate_limited()` |
| `jitter_ms` | `100` | Max random jitter added to delays |
| `initial_delay_ms` | `100` | Starting delay |

### `Throttle`

| Method / Property | Description |
|-------------------|-------------|
| `wait()` | Sleep for current delay; call before each API request |
| `success()` | Signal success; reduces delay toward minimum |
| `rate_limited()` | Signal 429; applies exponential backoff |
| `error()` | Signal generic error; mild delay increase |
| `current_delay_ms` | Current wait in milliseconds |
| `state` | `"normal"` / `"throttled"` / `"recovering"` |
| `stats() -> dict` | Snapshot of all counters |

### `ThrottledExecutor`

```python
ThrottledExecutor(func, throttle=None, max_retries=3)
```

Wraps any callable. Raises `RateLimitError` inside `func` to trigger retry logic. Non-`RateLimitError` exceptions are re-raised immediately (no retry).

### `AdaptiveThrottle`

```python
AdaptiveThrottle(target_latency_ms=500, window=10)
```

| Method / Property | Description |
|-------------------|-------------|
| `record(latency_ms)` | Feed an observed latency sample |
| `avg_latency_ms` | Rolling average over last `window` samples |
| `suggested_delay_ms` | `0` if avg < target; scales up linearly with overrun |

---

## States

```
normal ──rate_limited()──► throttled
   ▲                           │
   │        success()          │
   └────────────────────── recovering
```

---

## License

MIT
