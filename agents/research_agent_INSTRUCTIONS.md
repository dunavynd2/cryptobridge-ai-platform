# Research Agent Instructions

## Purpose
Researches NIST, RFCs, MITRE, Azure Security Docs. Outputs structured findings.

## Usage
```python
from agents.research_agent import research_task
result = research_task("TLS 1.3 certificate validation")
```

## Extension
- Integrate RAG/ChromaDB for knowledge base.
- Add web search tools.
- Ensure sources are cited.

## Example Output
See code for JSON structure.