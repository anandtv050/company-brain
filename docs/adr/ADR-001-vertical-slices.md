# ADR-001: Build in vertical slices, HRMS first

- **Date:** 2026-11-25
- **Status:** Accepted

## Context
The target is 8 fake systems (HRMS, CRM, tickets, timesheets, wiki, Git/CI, finance, chat)
with RAG, MCP, agents, triggers and evals on top. Building layer by layer (all data, then
all RAG, then all agents) leaves nothing demoable for weeks and hides integration problems.

## Decision
Build one system end-to-end through every layer before starting the next. HRMS goes first:
the `employees` table is the foundation every other system references, and HR has the
hardest RBAC (salary, performance, medical reasons).

## Alternatives
- Layer by layer: rejected, no working product until the end.
- CRM first: rejected, weaker RBAC story and depends on employees anyway.

## Consequences
- A demoable HR copilot by Dec 5.
- Some abstractions (tool registry, agent state) will be reworked when slice 2 arrives.
