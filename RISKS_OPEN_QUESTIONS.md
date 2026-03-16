# Risks and Open Questions

## Risks
- **Source quality drift:** forum content can be outdated or unofficially phrased; needs source validation and freshness checks.
- **Hallucination risk:** model may over-generalize from partial docs/tickets without strict citation enforcement.
- **Data leakage risk:** internal ticket snippets may contain sensitive data unless redaction and RBAC are strict.
- **MCP dependency risk:** demo/corporate MCP outages can reduce answer quality; fallback behavior is required.
- **Latency risk:** multi-source retrieval + generation may exceed real-time support expectations.
- **Change management risk:** agents may mistrust AI suggestions without explainability and confidence cues.

## Open Questions
- Which exact Zoho domains/accounts are considered “official” for Tier A?
- What minimum citation policy is required (per paragraph, per claim, or per answer)?
- What ticket fields are allowed for retrieval and display by role?
- What is the target SLA for interactive answers and live call suggestions?
- What transcript provider/format will be used for Phase 2 live call ingestion?
- What is the required security model for corporate MCP (network, auth, audit)?
- What widget SDK constraints apply for Zoho Desk and Zoho CRM embedding?
- Which metrics are launch-gating vs post-launch monitoring?
