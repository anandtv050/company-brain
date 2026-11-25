# ADR-003: Permission filter before retrieval

- **Date:** 2026-11-25
- **Status:** Accepted

## Context
RAG over HR documents mixes public policies with confidential ones (salary bands,
disciplinary guide). If restricted chunks are retrieved and then dropped, they can still
leak through ranking, logs or a bug in the filter.

## Decision
Every chunk carries `access_roles`, `department`, `location`, `sensitivity`. The retriever
adds these as SQL `WHERE` conditions before the vector and full-text search runs, using the
user context from the token. Chunks the user cannot see never leave the database.

## Alternatives
- Post-filter the top-k: rejected, lower recall (top-k fills with forbidden chunks) and leak risk.
- One index per role: rejected, duplicates data and breaks with multi-role users.

## Consequences
- Leak tests must cover RAG paths, not only API paths.
- Filtered search can be slower on large indexes; measure p95 in evals.
