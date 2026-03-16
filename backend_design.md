# Support Copilot Backend Design (Zoho)

## 1) API Spec (REST-first, MCP bridge)

Base URL: `/api/v1`

### 1.1 `POST /questions:answer`
Main orchestration endpoint for grounded answers.

**Purpose**
1. Accept customer question/context.
2. Retrieve approved official Zoho sources.
3. Rank + summarize sources.
4. Query MCP server for similar historical tickets.
5. Return grounded answer with citations + draft response.

**Request**
```json
{
  "request_id": "req_01J...", 
  "tenant_id": "tenant_acme",
  "session_id": "sess_123",
  "channel": "email",
  "question": {
    "text": "How do I reset MFA for a locked user?",
    "language": "en",
    "product": "Zoho One"
  },
  "customer_context": {
    "account_tier": "enterprise",
    "region": "US",
    "plan": "premium"
  },
  "constraints": {
    "max_sources": 8,
    "max_tokens": 1200,
    "temperature": 0.1,
    "citation_mode": "strict"
  },
  "options": {
    "include_draft_reply": true,
    "include_ticket_similars": true,
    "debug": false
  }
}
```

**Response**
```json
{
  "request_id": "req_01J...",
  "status": "ok",
  "answer": {
    "final": "You can reset MFA from Admin Console > Security...",
    "confidence": 0.87,
    "grounding_score": 0.91,
    "citations": [
      {
        "id": "src_1",
        "title": "Reset MFA for users",
        "url": "https://help.zoho.com/...",
        "snippet": "Admins can reset...",
        "rank": 1
      }
    ]
  },
  "draft_reply": {
    "subject": "Steps to reset MFA",
    "body": "Hi <Customer Name>,\nHere are the steps...",
    "tone": "professional"
  },
  "retrieval": {
    "sources_considered": 42,
    "sources_used": 6,
    "retrieval_latency_ms": 180
  },
  "ticket_similars": {
    "count": 3,
    "items": [
      {
        "ticket_id": "SUP-11823",
        "similarity": 0.82,
        "resolution_summary": "Reset org policy and re-enroll MFA"
      }
    ]
  },
  "warnings": [],
  "trace_id": "tr_abc123"
}
```

**Failure example (partial fallback)**
```json
{
  "request_id": "req_01J...",
  "status": "partial",
  "answer": {
    "final": "Based on official docs, try...",
    "confidence": 0.63,
    "grounding_score": 0.88,
    "citations": ["..."]
  },
  "warnings": [
    {
      "code": "MCP_UNAVAILABLE",
      "message": "Historical ticket lookup unavailable; response excludes similar tickets"
    }
  ],
  "trace_id": "tr_abc123"
}
```

---

### 1.2 `POST /sources:search`
Direct retrieval endpoint for approved Zoho sources.

**Request**
```json
{
  "tenant_id": "tenant_acme",
  "query": "reset MFA locked user",
  "product": "Zoho One",
  "filters": {
    "doc_types": ["help_center", "kb", "release_notes"],
    "locale": "en",
    "approved_only": true
  },
  "top_k": 20
}
```

**Response**
```json
{
  "items": [
    {
      "source_id": "src_1",
      "title": "Reset MFA for users",
      "url": "https://help.zoho.com/...",
      "score": 0.92,
      "published_at": "2025-02-13T00:00:00Z",
      "snippet": "Admins can reset...",
      "tags": ["mfa", "security"]
    }
  ]
}
```

---

### 1.3 `POST /sources:rank-summarize`
Ranks candidate sources and emits condensed evidence set.

**Request**
```json
{
  "question": "How do I reset MFA for a locked user?",
  "candidates": [
    {"source_id": "src_1", "title": "...", "content": "..."}
  ],
  "max_evidence": 8
}
```

**Response**
```json
{
  "evidence": [
    {
      "source_id": "src_1",
      "rank": 1,
      "relevance": 0.94,
      "summary": "Step-by-step admin flow to reset user MFA.",
      "quote": "Admins can reset MFA from..."
    }
  ]
}
```

---

### 1.4 `POST /tickets:similar` (MCP-backed)
Retrieves semantically similar historical support tickets.

**Request**
```json
{
  "tenant_id": "tenant_acme",
  "query": "reset MFA locked user",
  "top_k": 5,
  "include_internal_notes": false
}
```

**Response**
```json
{
  "items": [
    {
      "ticket_id": "SUP-11823",
      "similarity": 0.82,
      "issue_summary": "User locked out after policy change",
      "resolution_summary": "Reset org policy and force re-enrollment",
      "links": ["https://desk.zoho.com/.../SUP-11823"]
    }
  ],
  "source": "mcp:historical-ticket-server"
}
```

---

### 1.5 `POST /transcripts:ingest` (future-ready)
Ingests live or batched transcript segments for near-real-time co-pilot context.

**Request**
```json
{
  "session_id": "chat_778",
  "tenant_id": "tenant_acme",
  "stream_id": "stream_45",
  "segments": [
    {
      "segment_id": "seg_1",
      "speaker": "customer",
      "start_ms": 0,
      "end_ms": 4200,
      "text": "I changed phones and now MFA fails"
    }
  ],
  "mode": "append",
  "sequence": 12,
  "timestamp": "2026-03-16T13:25:18Z"
}
```

**Response**
```json
{
  "accepted": true,
  "ingested_segments": 1,
  "conversation_state_version": 19
}
```

---

### 1.6 `GET /health`, `GET /ready`, `GET /metrics`
- `health`: process alive.
- `ready`: dependencies reachable (vector store, MCP bridge, LLM gateway).
- `metrics`: Prometheus scrape endpoint.


## 2) Service Boundaries

### API Gateway / Edge Service
- AuthN/AuthZ, rate limiting, tenant routing, request ID propagation.
- Enforces schema validation.

### Orchestrator Service
- Implements `/questions:answer` workflow.
- Manages retries/fallback path.
- Calls retrieval, ranking, MCP adapter, and answer composer.

### Source Retrieval Service
- Query rewrite + hybrid retrieval over approved Zoho corpus.
- Guarantees allowlisted domains and approved doc classes only.

### Ranking & Summarization Service
- Reranks candidates; creates extractive evidence summaries.
- Produces provenance map (`source_id -> quote offsets`).

### MCP Adapter Service
- Encapsulates MCP protocol/session handling.
- Normalizes similar-ticket data from MCP server.

### Answer Composer Service
- Produces grounded final answer + citations.
- Optional draft customer reply generation.
- Refuses unsupported claims when evidence below threshold.

### Transcript Ingestion Service
- Handles chunk ordering, dedupe, incremental context windows.
- Publishes updates to conversation state store.

### Shared Platform Components
- **Policy/Guardrails**: citation strictness, PII redaction, safe completion rules.
- **Cache**: short TTL query/result caching.
- **Observability**: logs, metrics, traces.


## 3) Auth and Environment Config

### Authentication/Authorization
- External clients: OAuth2/OIDC JWT bearer tokens.
- Service-to-service: mTLS + workload identity/JWT.
- Mandatory claims: `sub`, `tenant_id`, `scope`.
- Example scopes:
  - `copilot.answer:write`
  - `copilot.sources:read`
  - `copilot.tickets:read`
  - `copilot.transcripts:write`

### Tenant Isolation
- Tenant ID required on every write/read operation.
- Enforce tenant filters at datastore + query layer.

### Environment Variables (example)
```bash
APP_ENV=prod
API_PORT=8080
LOG_LEVEL=info
AUTH_ISSUER_URL=https://auth.example.com/
AUTH_AUDIENCE=zoho-support-copilot
MCP_SERVER_URL=https://mcp.internal/tickets
MCP_TIMEOUT_MS=1500
VECTOR_DB_URL=http://vectordb:6333
VECTOR_COLLECTION=zoho_approved_docs
LLM_GATEWAY_URL=https://llm-gateway.internal
LLM_MODEL_ANSWER=gpt-4.1-mini
LLM_MODEL_RERANK=rerank-v1
REDIS_URL=redis://redis:6379
CITATION_MIN_GROUNDING_SCORE=0.75
FEATURE_TRANSCRIPT_INGEST=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
```


## 4) Logging and Observability

### Structured Logging
- JSON logs with: `timestamp`, `level`, `service`, `trace_id`, `span_id`, `tenant_id`, `request_id`, `route`, `latency_ms`, `status`.
- Never log raw secrets/tokens.
- Redact PII fields (`email`, `phone`, `customer_name`).

### Metrics (Prometheus)
- `http_requests_total{route,status}`
- `http_request_duration_ms_bucket{route}`
- `retrieval_latency_ms`
- `mcp_call_latency_ms`
- `mcp_call_failures_total`
- `grounding_score_histogram`
- `fallback_invocations_total{reason}`
- `draft_reply_generation_total{status}`

### Distributed Tracing
- OpenTelemetry traces across all services.
- Required spans:
  - `orchestrate.answer`
  - `retrieve.sources`
  - `rank.summarize`
  - `mcp.similar_tickets`
  - `compose.answer`


## 5) Error Handling and Fallback Behavior

### Error Model (uniform)
```json
{
  "error": {
    "code": "MCP_TIMEOUT",
    "message": "Historical ticket service timed out",
    "retryable": true,
    "details": {"timeout_ms": 1500}
  },
  "trace_id": "tr_abc123"
}
```

### HTTP Mapping
- `400` validation/schema errors
- `401` unauthenticated
- `403` unauthorized scope/tenant
- `404` resource not found
- `409` idempotency/sequence conflict (transcript ingest)
- `422` cannot ground answer with required citation strictness
- `429` rate limited
- `500` internal error
- `502/503/504` dependency failures (MCP/LLM/vector DB)

### Fallback Strategy (for `/questions:answer`)
1. **MCP failure**: continue without ticket similars; set `status=partial`, add warning.
2. **Retriever low recall**: broaden filters once; if still low, return clarifying question.
3. **Ranker/LLM timeout**: use lexical ranking baseline + extractive snippets.
4. **Low grounding score**: suppress definitive answer; return safe next steps + ask for details.
5. **Draft reply failure**: still return grounded answer.


## 6) Schema Definitions (JSON Schema-style)

```yaml
QuestionRequest:
  type: object
  required: [tenant_id, session_id, question]
  properties:
    request_id: {type: string}
    tenant_id: {type: string}
    session_id: {type: string}
    channel: {type: string, enum: [email, chat, voice, web]}
    question:
      type: object
      required: [text]
      properties:
        text: {type: string, minLength: 3, maxLength: 8000}
        language: {type: string}
        product: {type: string}
    customer_context:
      type: object
      additionalProperties: true
    constraints:
      type: object
      properties:
        max_sources: {type: integer, minimum: 1, maximum: 20, default: 8}
        max_tokens: {type: integer, minimum: 200, maximum: 4000, default: 1200}
        temperature: {type: number, minimum: 0, maximum: 1, default: 0.1}
        citation_mode: {type: string, enum: [strict, best_effort], default: strict}
    options:
      type: object
      properties:
        include_draft_reply: {type: boolean, default: true}
        include_ticket_similars: {type: boolean, default: true}
        debug: {type: boolean, default: false}

QuestionResponse:
  type: object
  required: [request_id, status, answer, trace_id]
  properties:
    request_id: {type: string}
    status: {type: string, enum: [ok, partial, failed]}
    answer:
      type: object
      required: [final, confidence, grounding_score, citations]
      properties:
        final: {type: string}
        confidence: {type: number}
        grounding_score: {type: number}
        citations:
          type: array
          items:
            type: object
            required: [id, title, url, rank]
            properties:
              id: {type: string}
              title: {type: string}
              url: {type: string, format: uri}
              snippet: {type: string}
              rank: {type: integer}
    draft_reply:
      type: object
      properties:
        subject: {type: string}
        body: {type: string}
        tone: {type: string}
    warnings:
      type: array
      items:
        type: object
        properties:
          code: {type: string}
          message: {type: string}
    trace_id: {type: string}
```


## 7) Architecture Diagram (Markdown)

```text
                        +------------------------------+
Client (Agent UI/API) ->| API Gateway / Auth / Limits |
                        +--------------+---------------+
                                       |
                                       v
                           +-----------+-----------+
                           |   Orchestrator        |
                           | (/questions:answer)   |
                           +-----+----+----+-------+
                                 |    |    |
              +------------------+    |    +-------------------+
              |                       |                        |
              v                       v                        v
   +---------------------+   +----------------------+   +------------------+
   | Source Retrieval    |   | Rank & Summarize     |   | MCP Adapter      |
   | (approved Zoho KB)  |   | (evidence builder)   |   | (similar tickets)|
   +----------+----------+   +----------+-----------+   +--------+---------+
              |                         |                        |
              v                         v                        v
      +---------------+          +-------------+         +---------------+
      | Vector / BM25 |          | LLM Gateway |         | MCP Server    |
      | index/store   |          | (rerank/sum)|         | (ticket data) |
      +---------------+          +-------------+         +---------------+
                                 \
                                  \ evidence + similars
                                   v
                          +-----------------------+
                          | Answer Composer       |
                          | grounded + citations  |
                          +-----------+-----------+
                                      |
                                      v
                                API Response

Future path:
  Transcript Stream -> Transcript Ingestion -> Conversation State Store -> Orchestrator context
```


## 8) Suggested Folder Structure

```text
backend/
  cmd/
    api-server/
      main.go
  internal/
    api/
      handlers/
        questions.go
        sources.go
        tickets.go
        transcripts.go
      middleware/
        auth.go
        request_id.go
        ratelimit.go
      schemas/
        question_request.json
        question_response.json
        error.json
    orchestrator/
      pipeline.go
      fallback.go
    retrieval/
      retriever.go
      allowlist_policy.go
    ranking/
      reranker.go
      summarizer.go
    mcp/
      client.go
      adapter.go
    composer/
      answer_composer.go
      draft_reply.go
    transcript/
      ingest.go
      state_store.go
    platform/
      config/
        env.go
      logging/
        logger.go
      observability/
        metrics.go
        tracing.go
      errors/
        codes.go
      auth/
        verifier.go
  docs/
    api.md
    architecture.md
  openapi/
    support-copilot.yaml
  deploy/
    docker/
      Dockerfile
    k8s/
      deployment.yaml
      service.yaml
```

---

### Notes
- Design is REST-centric but compatible with RPC style (`/questions:answer`) for orchestration semantics.
- If you prefer strict OpenAPI-first delivery, lift these endpoint contracts directly into `openapi/support-copilot.yaml`.
