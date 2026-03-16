# Zoho Support Assistant Retrieval Design

## 1) Retrieval Design

### 1.1 Architecture and Data Separation
Use two physically separate indexes and one logical orchestrator:

1. **Official Public Index** (authoritative)
   - Sources:
     - Approved Zoho Help URLs (knowledge base, docs)
     - Approved Zoho community/forum URLs
   - Purpose:
     - Policy/How-to guidance for user-facing answers
   - Constraint:
     - Only URLs on an allowlist are ingestible.

2. **Internal Historical Tickets Index** (non-authoritative)
   - Sources:
     - Historical Desk tickets loaded through MCP
   - Purpose:
     - Example resolutions, troubleshooting patterns
   - Constraint:
     - Never treated as policy source.

3. **Retrieval Orchestrator**
   - Runs official-first retrieval pipeline.
   - Optionally augments with internal ticket examples.
   - Enforces output guardrails:
     - no final answer without official citations,
     - internal evidence labeled as historical examples.

---

### 1.2 Ingestion Strategy

#### A) Official Public Sources Ingestion
1. **Allowlist governance**
   - Maintain approved domain/path rules (e.g., `help.zoho.com/*`, approved `community.zoho.com/*` paths).
   - Reject out-of-scope URLs at crawl time.

2. **Crawling + extraction**
   - Crawl pages with canonical URL capture.
   - Parse title, headings, body, article last-updated date, product/module tags.
   - Strip navigation/boilerplate.

3. **Normalization**
   - Deduplicate by canonical URL + normalized text hash.
   - Convert to clean markdown/plaintext for chunking.

4. **Versioning**
   - Keep `doc_version` and `ingested_at`.
   - Soft-retire stale versions when page changes.

5. **Quality gates**
   - Reject very short or low-content pages.
   - Mark source type as `official_help` or `community_forum`.

#### B) Internal Historical Tickets Ingestion (MCP)
1. **Connector scope**
   - Pull resolved/closed tickets from approved Desk projects via MCP.

2. **Field extraction**
   - Ticket ID, product/module, issue summary, problem description, resolution text, timestamps, team, tags.

3. **PII/Sensitive redaction**
   - Redact names, emails, phone numbers, account IDs, secrets.
   - Keep structured placeholders for debugging context.

4. **Resolution filtering**
   - Exclude unresolved or non-actionable tickets.
   - Optional quality classifier to keep only high-signal examples.

5. **Retention policy**
   - Respect internal retention and compliance requirements.

---

### 1.3 Chunking Strategy

#### Official docs/forum chunking
- **Primary split:** heading-based sections.
- **Target chunk size:** 350–700 tokens.
- **Overlap:** 80–120 tokens to preserve context across boundaries.
- **Special handling:**
  - Keep lists/steps/procedures intact when possible.
  - Preserve table rows with nearby headers.
- **Store chunk lineage:** `doc_id`, `section_path`, `chunk_index`.

#### Ticket chunking
- Template-based chunks:
  1. **Issue context chunk** (symptoms, environment)
  2. **Actions taken chunk**
  3. **Final resolution chunk**
- **Target size:** 250–500 tokens (tickets are noisier).
- **No aggressive overlap** unless long narrative text exists.

---

### 1.4 Metadata Schema

Use a unified schema with strict source-type fields:

- `record_id` (unique)
- `source_family` (`official_public` | `internal_ticket`)
- `source_type` (`official_help` | `community_forum` | `desk_ticket`)
- `product` (e.g., Desk, CRM)
- `module` (e.g., automations, SLAs)
- `title`
- `url` (official/community only)
- `ticket_id` (internal only)
- `section_path`
- `chunk_index`
- `text`
- `language`
- `created_at`
- `updated_at`
- `ingested_at`
- `doc_version`
- `quality_score` (ingestion-time)
- `freshness_days` (derived)
- `permissions_scope` (for access control)
- `pii_redacted` (bool for ticket chunks)

---

## 2) Ranking Rules

### 2.1 Retrieval Pipeline (official-first)

1. **Query understanding**
   - Detect product/module intent, task type (how-to vs troubleshooting), and policy sensitivity.

2. **Stage 1: Official retrieval (mandatory first pass)**
   - Run hybrid retrieval (BM25 + dense embeddings) over `official_public` index only.
   - Return top-N candidates.

3. **Stage 2: Official reranking**
   - Cross-encoder reranker over top candidates.
   - Apply source priors:
     - `official_help` bonus,
     - `community_forum` penalty unless semantic match is very strong.

4. **Stage 3: Conditional ticket retrieval**
   - Only run if:
     - official evidence is insufficient for practical troubleshooting details, or
     - user asks for examples.
   - Retrieve from `internal_ticket` separately.

5. **Stage 4: Evidence assembly**
   - Build answer from official evidence first.
   - Add internal ticket snippets under a clearly labeled “Historical examples” section.

### 2.2 Scoring Formula (illustrative)

For each candidate chunk:

`final_score = 0.45 * dense_sim + 0.25 * bm25 + 0.20 * rerank + 0.05 * freshness + 0.05 * quality + source_prior`

Where source priors:
- `official_help`: `+0.10`
- `community_forum`: `-0.05` (can be offset by very high rerank score)
- `desk_ticket`: scored in separate pool; never outranks official in primary evidence list.

### 2.3 Hard ranking constraints
- At least one `official_help`/approved official public citation must exist to produce policy/how-to answer.
- Community/forum chunks cannot be sole evidence for policy claims.
- Internal ticket chunks cannot be used as normative guidance.

---

## 3) Citation Generation Method

### 3.1 Citation requirements
- Every user-facing answer must include official source URLs used.
- Citations map each claim cluster to specific official chunk(s).
- Internal ticket citations (if shown) must be marked as historical and internal.

### 3.2 Citation format

Recommended rendered format:

- **Official:** `[O1] <Article Title> — <URL>`
- **Community (if used):** `[C1] <Thread Title> — <URL> (community)`
- **Historical internal:** `[H1] Desk Ticket #<id> (historical example, not policy)`

In answer body:
- Append inline references like `(see [O1], [O2])`.
- For historical statements: `(historical example: [H1])`.

### 3.3 Claim-to-evidence alignment
- Before final output, run claim verifier:
  - each actionable/policy claim must map to ≥1 official citation.
  - unmatched claims are removed or rewritten with uncertainty language.

---

## 4) Preventing Unsupported Answers

Implement answer-time guardrails:

1. **Evidence threshold gate**
   - If no official evidence above confidence threshold, do not provide definitive instructions.
   - Respond with safe fallback:
     - “I could not verify this in approved Zoho documentation.”

2. **Unsupported-claim detector**
   - Check generated answer sentences against retrieved spans.
   - Flag hallucinated claims (no lexical/semantic support).

3. **Policy source gate**
   - Any policy/configuration recommendation requires official citation.
   - Community-only support allowed only for non-policy tips and must be labeled.

4. **Ticket-use gate**
   - Internal tickets only in “Historical examples” subsection.
   - Never state “Zoho policy is…” from internal evidence.

5. **Abstain behavior**
   - If evidence is conflicting or low-confidence:
     - present verified partial answer,
     - list unknowns,
     - suggest escalation/check in official portal.

---

## 5) Confidence Scoring

Compute confidence as a calibrated score in `[0, 1]` with bands:

- **High (>=0.80):**
  - multiple consistent official_help citations,
  - strong rerank scores,
  - low contradiction.

- **Medium (0.60–0.79):**
  - at least one solid official citation,
  - some ambiguity or partial coverage.

- **Low (<0.60):**
  - weak/indirect official support,
  - heavy reliance on community or historical tickets.

### Suggested confidence components

`confidence = 0.40 * official_evidence_strength + 0.20 * citation_coverage + 0.20 * consistency + 0.10 * freshness + 0.10 * query_match`

Penalties:
- `-0.15` if no official_help citation.
- `-0.10` if answer relies primarily on community.
- `-0.20` if any key claim unsupported.

Use confidence to control tone:
- High: direct guidance.
- Medium: guidance + caveats.
- Low: abstain/clarify/escalate.

---

## 6) Evaluation Checklist

Use this checklist for acceptance testing of retrieval quality and safety.

### 6.1 Source separation and compliance
- [ ] Official and internal indexes are physically/logically separate.
- [ ] Access controls prevent cross-scope leakage.
- [ ] Ticket data is redacted and tagged `internal_ticket`.

### 6.2 Retrieval priority behavior
- [ ] Official help results appear before community for equivalent relevance.
- [ ] Community is only promoted when significantly more relevant.
- [ ] Internal tickets never displace official sources in policy answers.

### 6.3 Citation correctness
- [ ] Every final answer includes official URL citations.
- [ ] Each actionable claim maps to at least one official citation.
- [ ] Community citations are labeled as community.
- [ ] Internal examples are labeled “historical example, not policy.”

### 6.4 Unsupported-answer prevention
- [ ] No-answer/abstain triggered when official evidence is missing.
- [ ] Hallucination detector catches unsupported claims.
- [ ] Conflicting evidence triggers cautious response.

### 6.5 Confidence calibration
- [ ] Confidence correlates with human-judged correctness.
- [ ] Low-confidence responses are more conservative.
- [ ] Thresholds are tuned using held-out queries.

### 6.6 Offline + online evaluation
- [ ] Offline metrics: Recall@k, nDCG@k, citation precision, unsupported-claim rate.
- [ ] Scenario tests: policy question, troubleshooting question, edge/unknown question.
- [ ] Online metrics: user satisfaction, deflection success, escalation rate, correction rate.

