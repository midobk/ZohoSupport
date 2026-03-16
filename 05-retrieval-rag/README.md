# Workstream 5: Retrieval / RAG

## Goal
Deliver accurate, citation-grounded responses using trusted support knowledge.

## Corpus Priorities
- Product docs, internal troubleshooting guides, approved macros, policy docs.
- Exclude stale/unreviewed content by default.

## Pipeline Plan
- Ingestion + normalization with metadata tags (product, version, policy level).
- Chunking strategy tuned for support procedures.
- Hybrid retrieval (semantic + keyword).
- Reranking and source filtering before generation.

## Quality Controls
- Citation requirement for any factual claim.
- Low-confidence fallback when retrieval quality is weak.
- Source freshness checks and deprecation flags.

## Evaluation Inputs
- Gold set of historical tickets with accepted resolutions.
- Hallucination and citation-accuracy scorecards.

## Open Questions
- Do we use one index per product or shared index with strict filters?
