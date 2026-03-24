# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅        |

## Reporting a Vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, email the maintainer directly (address in `pyproject.toml`) with:

1. A description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (optional)

You will receive an acknowledgement within 48 hours and a fix within 14 days for confirmed issues.

## Scope

`agent-throttle` is a pure Python throttling library with no network access of its own. Security concerns are most likely to involve:

- Denial of service via runaway retry loops (mitigated by `max_retries` and `max_delay_ms`)
- Timing side-channels in delay values (jitter is intentional to prevent thundering herd)
