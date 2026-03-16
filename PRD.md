# PRD — Zoho Support Copilot

## 1) Product Overview
Build a support copilot for Zoho pre-sales/support teams that provides fast, source-linked answers from official Zoho content, and evolves into a call-assist + internal case-reuse assistant.

## 2) Problem Statement
Agents spend too long searching help docs/forums, re-solving known issues from old tickets, and drafting responses during live conversations.

## 3) Goals & Non-Goals
### Goals
- Return concise, accurate answers with citations to official Zoho sources.
- Support retrieval of similar historical support cases from ticket data (via MCP).
- Prepare architecture for live call guidance and Zoho Desk/CRM embedding.

### Non-Goals (MVP)
- Autonomous ticket actions (close/update/assign).
- Fully automated real-time voice bot responses.
- Deep analytics dashboards.

## 4) Scope by Phase
### MVP (Phase 1)
- Web app UI for question input and answer output.
- Retrieval + answering from official Zoho help/forum pages.
- Source links shown inline per answer.
- MCP integration with **demo MCP server** for historical ticket retrieval (read-only).
- Suggested draft answer that combines official sources + similar ticket context.
- Basic role-based access and audit logs.

### Phase 2
- Switch connector from demo MCP to corporate MCP server with configuration toggle.
- Live call listener (streaming transcript ingestion) + real-time suggested responses.
- Feedback capture (thumbs up/down, edit distance, accepted suggestion).
- Team workspace controls (allowed products, escalation prompts, confidence thresholds).

### Phase 3
- Embeddable widget for Zoho Desk and Zoho CRM.
- Contextual side-panel suggestions based on current ticket/CRM record.
- Enterprise controls (SSO, tenant isolation hardening, policy packs).

## 5) Users & Roles
- **Support Agent (primary):** asks questions, uses drafts, responds to customers.
- **Support Lead/Manager:** configures defaults, reviews usage/quality, tunes guardrails.
- **Admin/IT/Security:** sets MCP endpoints, auth, access policy, and data governance.

## 6) Core User Flows
1. **Ask & Answer from Official Sources**
   - Agent enters customer question → app retrieves Zoho help/forum content → app returns concise answer + links.
2. **Find Similar Cases via MCP**
   - Agent clicks “Find similar tickets” → app queries MCP server → returns top related historical cases with metadata.
3. **Draft Response Generation**
   - Agent requests draft → app composes customer-ready response using official sources + ticket learnings (clearly labeled).
4. **Live Call Assist (Phase 2)**
   - Agent joins/starts call session → transcript stream arrives → app pushes suggested answers and references in near real time.
5. **Embedded Assist (Phase 3)**
   - Agent opens Zoho Desk/CRM widget → context auto-populates from current record → app suggests tailored response.

## 7) Functional Requirements & Acceptance Criteria
### F1: Official Source Answering
- System searches approved Zoho help/forum sources.
- Response includes at least 1 citation URL per factual claim block.

**Acceptance Criteria**
- Given a valid question, when searched, then answer is returned within target latency and includes clickable official links.
- Given no reliable source match, then app responds with “insufficient official evidence” rather than fabricating.

### F2: MCP Similar Ticket Retrieval (Demo First)
- System queries demo MCP server for similar historical tickets.
- Returns top N similar tickets with title, summary, relevance score.

**Acceptance Criteria**
- Given MCP availability, when “Find similar tickets” is used, then top results are displayed with identifiers and relevance ordering.
- Given MCP failure/timeout, then user receives a clear fallback message; official-source answering still works.

### F3: Draft Answer Composer
- System generates editable draft reply with sections: “Official guidance” and “Internal precedent”.

**Acceptance Criteria**
- Draft content is editable before copy/export.
- Output clearly labels internal ticket-derived statements and never presents them as official policy.

### F4: MCP Endpoint Switch (Phase 2)
- Admin can configure endpoint/profile for demo vs corporate MCP.

**Acceptance Criteria**
- Endpoint can be switched by config without app code changes.
- Connection test validates auth and schema compatibility before enablement.

### F5: Live Call Suggestion Engine (Phase 2)
- System ingests transcript chunks and continuously suggests next best responses.

**Acceptance Criteria**
- New suggestion appears within defined SLA from transcript update.
- Each suggestion includes confidence and source attribution.

### F6: Embedded Widget (Phase 3)
- Widget runs inside Zoho Desk/CRM with current ticket/contact context.

**Acceptance Criteria**
- Widget loads with authenticated user context.
- Suggestions reference current record fields (product, issue type, account tier).

## 8) Trust & Safety Boundaries
### Source Tiers
- **Tier A (Official):** Zoho help center, official docs, official forum posts/accounts.
- **Tier B (Internal):** historical Zoho Desk tickets via MCP.

### Policy Rules
- Official answers should prioritize Tier A evidence.
- Tier B may inform suggestions but must be explicitly labeled “internal precedent.”
- Conflicts between Tier A and Tier B resolve in favor of Tier A.
- No internal ticket content shown to unauthorized roles.
- Redact/mask sensitive fields (PII/secrets) from retrieved ticket context before generation.
- If confidence is low or sources conflict, model should ask clarifying questions or recommend escalation.

## 9) Success Metrics
- First-response preparation time reduction (%).
- Citation coverage rate (% answers with valid official links).
- Suggestion acceptance rate (% copied/used drafts).
- Hallucination/error rate from QA sampling.
- Agent satisfaction (CSAT/NPS internal).

## 10) Out of Scope Clarifications
- Not replacing human agent judgment.
- Not legal/compliance source of truth by itself.
- Not handling proactive outbound campaigns.
