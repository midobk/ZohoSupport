# Workstream 4: Backend / API

## Goal
Provide reliable APIs for context assembly, response generation, feedback, and audit.

## Proposed Services
- API Gateway for auth, routing, rate limits.
- Copilot Orchestrator service for prompt and tool orchestration.
- Support Metadata service for ticket/user/org context.

## API Surface (v1)
- `POST /copilot/suggest` -> returns draft, citations, confidence.
- `POST /copilot/feedback` -> stores rating and reason.
- `GET /copilot/history/:ticketId` -> audit and prior suggestions.
- `GET /health` and service telemetry endpoints.

## Engineering Constraints
- Request tracing across all hops.
- P95 latency target < 3s for first token.
- Idempotency keys for retried generation requests.

## Data Considerations
- Minimize PII persistence; store references where possible.
- Versioned prompt/template configs.

## Open Questions
- Single deployable service vs split microservices at v1?
