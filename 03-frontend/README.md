# Workstream 3: Frontend

## Goal
Build a maintainable web client for the support-copilot interface.

## Proposed Stack
- React + TypeScript.
- State/query: TanStack Query + lightweight local state.
- Styling: design-token driven component system.

## Architecture
- `app/` shell and routing.
- `features/copilot/` for suggestion lifecycle.
- `features/feedback/` for quality signals.
- API service layer with typed contracts.

## v1 Frontend Capabilities
- Ticket context ingestion into copilot panel.
- Streamed response rendering for faster perceived latency.
- Edit + accept flow for generated drafts.
- Feedback capture and local optimistic updates.

## Definition of Done
- Type-safe API integration.
- Error boundaries and retry states.
- Component tests for critical flows.

## Open Questions
- Should streaming be SSE-only or SSE + websocket fallback?
