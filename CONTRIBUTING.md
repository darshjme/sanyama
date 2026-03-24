# Contributing

## Setup

```bash
git clone https://github.com/example/agent-throttle
cd agent-throttle
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests must pass. No new dependencies without discussion.

## Guidelines

- **Zero runtime deps** — stdlib only.
- **Type-annotated** — all public APIs must have type hints.
- **Tested** — every new behaviour needs a matching test.
- **Deterministic tests** — mock `time.sleep` and `random.uniform` where needed.

## Pull Requests

1. Fork and create a feature branch.
2. Write tests first (TDD preferred).
3. Run the full test suite.
4. Open a PR with a clear description of what and why.

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
