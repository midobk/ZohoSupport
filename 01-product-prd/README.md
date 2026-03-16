# Workstream 1: Product / PRD

## Goal
Define a v1 support-copilot product that helps Zoho support teams resolve tickets faster with consistent, policy-safe responses.

## Scope
- Core user personas: Support Agent, Team Lead, Admin.
- Primary jobs: draft reply, surface knowledge, suggest next best action, summarize thread.
- Success metrics: first-response time, time-to-resolution, CSAT, agent adoption.

## v1 Requirements
- In-ticket copilot panel with context-aware suggestions.
- One-click draft insertion and editable response modes.
- Citation-backed answers from trusted internal KB sources.
- Confidence indicator with escalation recommendation.
- Audit trail for generated suggestions.

## Non-Goals (v1)
- Fully autonomous ticket closure.
- Voice support.
- Multi-lingual parity beyond English baseline.

## Key Decisions
- Start with human-in-the-loop assistance only.
- Optimize for accuracy and explainability over creativity.
- Ship in phased rollout: pilot team -> expanded team -> org-wide.

## Open Questions
- Which Zoho products are in first release scope (Desk only vs Desk + CRM)?
- What policy/compliance jurisdictions are mandatory at launch?
