<div align="center">
<img src="assets/hero.svg" width="100%"/>
</div>

# agent-throttle

**Adaptive throttling for LLM API calls for LLM agents. Zero external dependencies.**

[![PyPI](https://img.shields.io/pypi/v/agent-throttle?color=blue)](https://pypi.org/project/agent-throttle/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero deps](https://img.shields.io/badge/dependencies-zero-brightgreen)](pyproject.toml)

---

## The Problem

Production LLM agents fail silently. Without adaptive throttling for llm api calls, you get undefined behaviour at scale — race conditions, lost state, cascading failures, and no way to debug what went wrong.

`agent-throttle` gives you a production-ready adaptive throttling for llm api calls primitive with a clean API, tested edge cases, and zero configuration.

## Installation

```bash
pip install agent-throttle
```

Or from source:

```bash
git clone https://github.com/darshjme/agent-throttle.git
cd agent-throttle
pip install -e .
```

## Quick Start

```python
from agent_throttle import *  # see API reference below

# See examples/ directory for complete working examples
```

## API Reference

The main classes and functions are defined in `agent_throttle/__init__.py`.

Key exports: `Backoff · jitter · AdaptiveThrottle · ThrottledExecutor`

All classes follow a consistent interface:
- Instantiate with sensible defaults
- Compose with other arsenal libraries
- Zero external dependencies required

See the source code and `tests/` directory for verified usage examples.

## How It Works

```mermaid
flowchart LR
    A[Agent Task] --> B[agent-throttle]
    B --> C{Decision}
    C -->|success| D[✅ Result]
    C -->|failure| E[⚠️ Handle]
    E --> B

    style B fill:#161b22,stroke:#cc9933,stroke-width:2,color:#cc9933
    style D fill:#1a3320,stroke:#238636,color:#3fb950
    style E fill:#3d1a1a,stroke:#f85149,color:#f85149
```

```mermaid
sequenceDiagram
    participant Agent
    participant AgentThrottle as agent-throttle
    participant Output

    Agent->>AgentThrottle: initialize()
    AgentThrottle-->>Agent: ready

    loop Agent Run
        Agent->>AgentThrottle: process(input)
        AgentThrottle-->>Agent: result
    end

    Agent->>Output: deliver(result)
```

## Philosophy

*Sthitaprajña* — one of steady wisdom moves without haste. agent-throttle enforces that steadiness on your API calls.

---

## Part of the Arsenal

`agent-throttle` is one of six production libraries for LLM agents:

| Library | Purpose |
|---------|---------|
| [herald](https://github.com/darshjme/herald) | Semantic task routing |
| [engram](https://github.com/darshjme/engram) | Agent memory |
| [sentinel](https://github.com/darshjme/sentinel) | ReAct loop guards |
| [verdict](https://github.com/darshjme/verdict) | Agent evaluation |
| [agent-guardrails](https://github.com/darshjme/agent-guardrails) | Output validation |
| [agent-observability](https://github.com/darshjme/agent-observability) | Tracing & metrics |

→ [arsenal](https://github.com/darshjme/arsenal) — the complete stack

---

*Built by [Darshankumar Joshi](https://github.com/darshjme), Gujarat, India.*
