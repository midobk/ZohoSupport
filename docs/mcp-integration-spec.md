# MCP Integration Layer Design for Support Copilot

## 1) Interface Spec

### 1.1 Goals
- Allow the support-copilot app to call a stable internal API independent of MCP server vendor.
- Support immediate integration with a demo MCP server.
- Enable future cutover to a corporate Zoho MCP server by changing configuration and adapter implementation only.

### 1.2 Core Abstraction
Define an internal `SupportMcpGateway` interface used by the app domain layer.

```ts
// App-facing contract (stable)
export interface SupportMcpGateway {
  searchTickets(input: SearchTicketsInput, ctx: RequestContext): Promise<SearchTicketsOutput>;
  getTicketDetails(input: GetTicketDetailsInput, ctx: RequestContext): Promise<GetTicketDetailsOutput>;
  findSimilarCases(input: FindSimilarCasesInput, ctx: RequestContext): Promise<FindSimilarCasesOutput>;
  summarizeResolutionPatterns(input: SummarizeResolutionPatternsInput, ctx: RequestContext): Promise<SummarizeResolutionPatternsOutput>;
}
```

The app imports only this interface and DTOs, never vendor-specific MCP tool names or transport details.

### 1.3 Data Contracts (Tool Contracts)

#### `search_tickets`
**Purpose:** Query tickets by text and optional structured filters.

Input:
```json
{
  "query": "payment failed after card update",
  "filters": {
    "status": ["open", "pending"],
    "priority": ["high"],
    "product": ["Billing"],
    "created_after": "2026-01-01T00:00:00Z",
    "created_before": "2026-03-01T00:00:00Z"
  },
  "page": {
    "size": 25,
    "cursor": null
  }
}
```

Output:
```json
{
  "results": [
    {
      "ticket_id": "TCK-10293",
      "subject": "Card update caused recurring charge failure",
      "status": "open",
      "priority": "high",
      "product": "Billing",
      "created_at": "2026-02-13T14:22:00Z",
      "snippet": "Customer updated card, subscription renewals began failing with code 3DS_REQUIRED..."
    }
  ],
  "next_cursor": "eyJwYWdlIjoyfQ==",
  "total_estimate": 124
}
```

#### `get_ticket_details`
**Purpose:** Retrieve full details for one ticket.

Input:
```json
{
  "ticket_id": "TCK-10293",
  "include": ["conversation", "events", "attachments_meta"]
}
```

Output:
```json
{
  "ticket": {
    "ticket_id": "TCK-10293",
    "subject": "Card update caused recurring charge failure",
    "status": "open",
    "priority": "high",
    "requester": {
      "id": "CUST-888",
      "name": "A. Rivera",
      "segment": "enterprise"
    },
    "conversation": [
      {
        "at": "2026-02-13T14:22:00Z",
        "author": "customer",
        "body": "Payments stopped after updating card details."
      }
    ],
    "events": [
      {
        "at": "2026-02-13T14:30:00Z",
        "type": "status_change",
        "from": "new",
        "to": "open"
      }
    ],
    "attachments_meta": []
  }
}
```

#### `find_similar_cases`
**Purpose:** Surface semantically related resolved tickets for faster diagnosis.

Input:
```json
{
  "ticket_id": "TCK-10293",
  "query_override": null,
  "limit": 10,
  "min_similarity": 0.72
}
```

Output:
```json
{
  "cases": [
    {
      "ticket_id": "TCK-99810",
      "similarity": 0.89,
      "resolution_summary": "Enabled 3DS flow and re-tokenized stored card.",
      "resolved_at": "2026-01-27T10:08:00Z"
    }
  ]
}
```

#### `summarize_resolution_patterns`
**Purpose:** Summarize common fixes and success rates across a case set.

Input:
```json
{
  "source": {
    "ticket_ids": ["TCK-99810", "TCK-99602", "TCK-99011"]
  },
  "group_by": ["root_cause", "fix_type"],
  "time_window_days": 180
}
```

Output:
```json
{
  "patterns": [
    {
      "root_cause": "3DS not completed",
      "fix_type": "re-authentication prompt",
      "count": 42,
      "success_rate": 0.93,
      "median_resolution_hours": 6.4
    }
  ],
  "narrative_summary": "Most billing failures were resolved by re-authentication and card token refresh."
}
```

### 1.4 Canonical Error Model
All adapters normalize transport/provider errors:

```json
{
  "error": {
    "code": "UPSTREAM_TIMEOUT",
    "message": "MCP tool call timed out",
    "retryable": true,
    "upstream": {
      "provider": "demo_mcp",
      "trace_id": "d2f5..."
    }
  }
}
```

Recommended internal codes: `INVALID_INPUT`, `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `RATE_LIMITED`, `UPSTREAM_TIMEOUT`, `UPSTREAM_UNAVAILABLE`, `INTERNAL_ERROR`.

---

## 2) Adapter Pattern

### 2.1 Components
- `SupportMcpGateway` (interface): stable app-facing API.
- `DemoMcpAdapter` (implementation): maps canonical contracts to demo MCP tools.
- `ZohoMcpAdapter` (implementation): maps canonical contracts to corporate Zoho MCP tools.
- `McpClient` (transport): generic MCP JSON-RPC/tool-call client.
- `AuthProvider` (strategy): supplies credentials/tokens for each provider.
- `PolicyMiddleware`: timeout, retry, audit, permission checks, and error normalization.

### 2.2 Call Flow
1. App service calls `SupportMcpGateway.searchTickets(...)`.
2. `PolicyMiddleware` validates permission scope (`tickets.read`, etc.).
3. Adapter transforms canonical input into provider-specific tool payload.
4. `McpClient` executes tool call with timeout/retry policy.
5. Adapter maps provider response to canonical output.
6. Audit event emitted with redacted fields.

### 2.3 Provider Mapping Table (Example)
| Canonical Contract | Demo MCP Tool | Zoho MCP Tool (target) |
|---|---|---|
| `search_tickets` | `demo.search_tickets` | `zoho.support.searchTickets` |
| `get_ticket_details` | `demo.get_ticket_details` | `zoho.support.getTicket` |
| `find_similar_cases` | `demo.find_similar_cases` | `zoho.support.findRelatedCases` |
| `summarize_resolution_patterns` | `demo.summarize_resolution_patterns` | `zoho.support.summarizeResolutionPatterns` |

Keep mappings in configuration, not app business logic.

---

## 3) Authentication Strategy

### 3.1 Principles
- Centralize auth behind `AuthProvider` interface.
- No hardcoded secrets in code.
- Use short-lived tokens where possible.
- Separate service identity from end-user identity.

### 3.2 Phase 1 (Demo MCP)
- Use static API key or simple bearer token from environment (`DEMO_MCP_API_KEY`).
- Inject credential per request through `AuthProvider`.
- Rotate keys by deployment config update.

### 3.3 Phase 2 (Corporate Zoho MCP)
- Prefer OAuth2 client credentials or mTLS + signed JWT (based on enterprise standard).
- Store client secret/cert in secret manager.
- Token caching with proactive refresh (e.g., refresh at 80% TTL).
- Optional on-behalf-of user token propagation for row-level access controls.

### 3.4 Auth Interface
```ts
export interface AuthProvider {
  getAuthHeaders(ctx: RequestContext, provider: "demo" | "zoho"): Promise<Record<string, string>>;
}
```

---

## 4) Timeout and Retry Behavior

### 4.1 Default Timeouts
- `search_tickets`: 2500 ms
- `get_ticket_details`: 3000 ms
- `find_similar_cases`: 4000 ms
- `summarize_resolution_patterns`: 5000 ms

### 4.2 Retry Policy
- Max retries: 2 (total attempts = 3)
- Backoff: exponential with jitter (e.g., 200ms, 500ms)
- Retry only on retryable failures: timeout, 429, transient 5xx, connection reset.
- Do **not** retry on 4xx validation/authz errors.

### 4.3 Circuit Breaker (Recommended)
- Open after threshold (e.g., 50% failures over 20 requests).
- Half-open probe after cool-down (e.g., 30s).
- Fallback to degraded response message in copilot UI.

---

## 5) Audit Logging and Permission Boundaries

### 5.1 Audit Events (Structured)
For every MCP operation log:
- `timestamp`
- `request_id` / trace id
- `actor` (agent/service/user)
- `tenant_id`
- `operation` (canonical tool name)
- `provider` (demo/zoho)
- `resource_ids` (ticket IDs)
- `latency_ms`
- `result` (success/failure + error code)

### 5.2 Redaction Rules
- Never log full ticket body, attachment content, auth headers, or raw PII.
- Mask requester email/phone.
- Keep minimal snippets with configurable max length (e.g., 160 chars).

### 5.3 Permission Model
- Enforce RBAC scopes before adapter call:
  - `tickets.search`
  - `tickets.read`
  - `cases.similarity.read`
  - `analytics.resolution.read`
- Add tenant boundary checks (`ctx.tenant_id` must match requested resources).
- Prefer deny-by-default if scope missing.

---

## 6) Mock Responses for Local Development

### 6.1 Local Mock Adapter
Implement `MockMcpAdapter` that satisfies `SupportMcpGateway` and returns deterministic fixtures.

Use cases:
- UI development without external MCP dependency
- integration tests for orchestration logic
- chaos testing by toggling mock error modes

### 6.2 Mock Modes
- `happy_path`: valid deterministic datasets
- `timeout_mode`: simulate `UPSTREAM_TIMEOUT`
- `auth_error_mode`: simulate `UNAUTHORIZED`
- `empty_results_mode`: zero matches

### 6.3 Example Mock Fixture
```json
{
  "search_tickets": {
    "results": [],
    "next_cursor": null,
    "total_estimate": 0
  }
}
```

Select mode via environment variable `MCP_ADAPTER_MODE=mock:happy_path`.

---

## 7) Migration Plan: Demo MCP → Corporate Zoho MCP

### Step 1: Freeze Canonical Contracts
- Finalize interface and DTO schema above.
- Add JSON-schema validation tests for all four tool contracts.

### Step 2: Implement Demo Adapter First
- Build `DemoMcpAdapter` and validate end-to-end in staging.
- Capture baseline latency, error rates, and audit coverage.

### Step 3: Build Zoho Adapter in Parallel
- Implement `ZohoMcpAdapter` using same `SupportMcpGateway` interface.
- Map Zoho-specific fields to canonical DTOs.

### Step 4: Conformance Test Suite
- Run identical contract tests against `DemoMcpAdapter`, `ZohoMcpAdapter`, and `MockMcpAdapter`.
- Ensure canonical outputs and error model consistency.

### Step 5: Shadow Traffic
- Mirror a percentage of non-mutating requests to Zoho adapter.
- Compare payload parity, latency, and failure types.

### Step 6: Controlled Cutover
- Feature flag `MCP_PROVIDER=zoho` per tenant/cohort.
- Start with low-risk tenant group.
- Roll forward if SLOs met; roll back by flag if regression detected.

### Step 7: Decommission Demo Provider
- Remove demo-specific secrets and endpoint config after stabilization window.
- Keep mock adapter for local dev and regression tests.

### Operational SLO Targets
- Availability: ≥ 99.9%
- p95 latency: ≤ 2.5s (`search_tickets`), ≤ 4s (`summarize_resolution_patterns`)
- Error budget policy tied to automated provider rollback flag.

---

## 8) Minimal Implementation Skeleton (Optional)

```ts
export class GatewayFactory {
  static create(cfg: Config): SupportMcpGateway {
    const client = new McpClient(cfg.transport);
    const auth = new CompositeAuthProvider(cfg.secrets);

    if (cfg.adapterMode.startsWith("mock")) {
      return new MockMcpAdapter(cfg.adapterMode);
    }

    const base = cfg.provider === "zoho"
      ? new ZohoMcpAdapter(client, auth)
      : new DemoMcpAdapter(client, auth);

    return new PolicyWrappedGateway(base, cfg.policy, cfg.audit);
  }
}
```

This factory keeps architecture stable while switching providers by configuration.
