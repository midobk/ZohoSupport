# Workstream 8: Evaluation / QA

## Goal
Create a measurable quality loop for model, retrieval, and product behavior.

## Test Layers
- Unit tests for prompt assembly and parsers.
- Integration tests for API + retrieval + tool chain.
- End-to-end tests for key agent workflows.

## Offline Evaluation
- Benchmark dataset from anonymized historical tickets.
- Metrics: factuality, citation precision/recall, helpfulness, safety violations.
- Regression gates before release promotion.

## Online Evaluation
- A/B or staged rollout with quality dashboards.
- User feedback correlation with resolution outcomes.
- Alerting for drift and latency degradation.

## Exit Criteria for v1
- Hallucination rate below agreed threshold.
- Stable latency SLO over 7-day window.
- No critical policy violations in pilot.

## Open Questions
- Which metric is release-blocking if tradeoffs occur?
