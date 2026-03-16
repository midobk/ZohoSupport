# Zoho Support-Copilot Orchestrator Summary

## Decisions (Parallel Discovery)
- Organized the initiative into 10 isolated workstream folders, one per agent scope.
- Prioritized a human-in-the-loop v1 for trust, with citation-backed suggestions.
- Chosen architecture direction: UI panel + orchestrated backend + retrieval grounding + MCP tools.
- Defined quality, safety, and privacy as release gates rather than post-launch add-ons.

## Workstream Outputs
1. Product/PRD: problem framing, v1 requirements, non-goals, success metrics.
2. UX/UI: panel-first interaction model, trust signals, accessibility baseline.
3. Frontend: React+TS feature architecture and critical interaction capabilities.
4. Backend/API: core endpoint plan, latency goals, traceability constraints.
5. Retrieval/RAG: ingestion, hybrid retrieval, reranking, citation controls.
6. MCP Integration: tool governance, schema contracts, failure handling.
7. Live Assist: real-time coaching scope and performance expectations.
8. Evaluation/QA: offline/online eval loops and release criteria.
9. Security/Privacy: RBAC, redaction, retention, audit and compliance baseline.
10. Widget Integration: host embedding strategy and SDK contract expectations.

## Changed Files
- `01-product-prd/README.md`
- `02-ux-ui/README.md`
- `03-frontend/README.md`
- `04-backend-api/README.md`
- `05-retrieval-rag/README.md`
- `06-mcp-integration/README.md`
- `07-live-assist/README.md`
- `08-evaluation-qa/README.md`
- `09-security-privacy/README.md`
- `10-widget-integration/README.md`
- `ORCHESTRATOR_SUMMARY.md`

## Open Questions (Cross-Cutting)
- Final launch surface scope: Zoho Desk only or Desk + CRM.
- Confidence presentation format and UX interaction for citations.
- Service topology for v1: modular monolith vs early microservices split.
- Retrieval indexing strategy across products and versions.
- Live Assist default behavior: always-on vs user-enabled.
- Enterprise requirements at launch: CMK, jurisdiction-specific controls.

## Risks
- Accuracy/trust risk if retrieval coverage or freshness is weak.
- Latency risk from synchronous orchestration + tool invocations.
- Adoption risk if UI adds friction to high-volume agent workflows.
- Compliance risk if redaction/retention are not implemented early.
- Integration risk from host product version differences for widget embedding.

## Proposed Implementation Order (Post-Discovery)
1. Product/PRD alignment + Security/Privacy baselines (scope and constraints locked).
2. Backend/API contracts + Retrieval/RAG skeleton (enable end-to-end data path).
3. Frontend shell + UX/UI core panel flow (connect to mocked then real APIs).
4. MCP integration for tool-backed context/actions with strict governance.
5. Evaluation/QA harness and baseline metrics wired into CI/release checks.
6. Live Assist incremental rollout on top of stable generation pipeline.
7. Widget integration hardening for host surfaces and phased deployment.
