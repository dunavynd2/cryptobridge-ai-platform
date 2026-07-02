# Testing Agent Instructions

## Purpose
Mandatory validator: Unit tests, linting (ruff), security (bandit/semgrep), dep reviews.

## Usage
```python
from agents.testing_agent import run_tests
results = run_tests('path/to/code')
```

## Cybersecurity Emphasis
Always scan for vulns in generated code.