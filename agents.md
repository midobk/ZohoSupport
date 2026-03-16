# AGENTS.md

## Mission
Build a runnable Zoho Support Copilot app.

## Global rules
- Prefer executable code over documentation
- Do not open docs-only PRs unless the task explicitly requests documentation
- Every implementation PR must include:
  - code changes
  - wiring to existing app flow where relevant
  - tests
  - local run instructions in PR description
- Keep official Zoho sources separate from historical tickets in UI and API
- Never return uncited official answers
- Use mock data where external integrations are not yet available
- Keep PRs scoped to one workstream
