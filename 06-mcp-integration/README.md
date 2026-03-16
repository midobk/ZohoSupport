# Workstream 6: MCP Integration

## Goal
Connect copilot orchestration to MCP-compatible tools/data providers safely.

## Candidate MCP Servers
- Knowledge search provider.
- Ticket metadata/context provider.
- Actions provider (macros, internal runbooks).

## Integration Approach
- Define strict tool registry and allowed operations.
- Contract-test each MCP server response schema.
- Add timeout, retry, and circuit breaker policy per tool.

## Safety and Governance
- Tool call allowlist by tenant and role.
- Prompt/tool trace logging with redaction.
- Detect and block high-risk tool outputs (policy violations).

## Deliverables
- MCP capability matrix.
- Tool invocation policy spec.
- Failure handling playbook.

## Open Questions
- Should tools run synchronously in request path or via async planner step?
