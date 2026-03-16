# Workstream 10: Widget Integration

## Goal
Embed support-copilot capabilities into Zoho support surfaces as a reusable widget.

## Integration Targets
- Zoho Desk ticket detail panel.
- Optional CRM context panel for account-aware support.

## Widget Requirements
- Lightweight initialization with host-provided context.
- Versioned SDK contract for host-to-widget communication.
- Theming support aligned with host app style tokens.

## Operational Requirements
- Feature flags for gradual rollout.
- Host-side telemetry hooks.
- Safe fallback when copilot backend unavailable.

## Deliverables
- Widget API contract draft.
- Embed guide and lifecycle events.
- Compatibility matrix across supported host versions.

## Open Questions
- Do we require offline mode behavior inside host products?
