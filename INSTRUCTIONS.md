# Project Instructions

## Setup
1. `git clone https://github.com/dunavynd2/cryptobridge-ai-platform.git`
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill keys (especially for models).
4. `python orchestrator.py` or `streamlit run frontend/app.py`

## Spec Sheets
See `specs/` directory for examples (e.g., `pki-management-microservice.md`). Use these as input for agents.

## Extending Agents
See individual `agents/*_INSTRUCTIONS.md` files.

## Development Workflow
Follow the autonomous loop in orchestrator. Use spec sheets to guide Coding Agent.

## .gitignore
Updated with security best practices — review before committing sensitive files.

For full vision, refer to original pasted text and `README.md`.