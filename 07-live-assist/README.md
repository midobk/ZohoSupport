# Workstream 7: Live Assist

## Goal
Provide real-time coaching for active agent conversations.

## Core Features
- Suggested next response while agent types.
- Intent/risk cues (escalation, refund policy, legal-sensitive language).
- Conversation summary refresh after each customer turn.

## Performance Targets
- Sub-1.5s incremental suggestion updates.
- Graceful degradation to manual request mode when under load.

## UX Guardrails
- Never auto-send messages.
- Show "draft generated" status and confidence.
- Preserve agent agency with easy dismiss/regenerate.

## Dependencies
- Streaming backend endpoint.
- Real-time event handling in frontend.
- RAG fast-path for top documents.

## Open Questions
- Should live assist be always-on or user-toggle default off?
