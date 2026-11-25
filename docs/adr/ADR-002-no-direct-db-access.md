# ADR-002: The AI never touches a database directly

- **Date:** 2026-11-25
- **Status:** Accepted

## Context
Real enterprise systems are reached through their APIs, and each system owns its data.
Letting an agent run SQL on `hrms_db` would bypass RBAC and make every leak a prompt problem.

## Decision
Agent → MCP server → system API → database. MCP servers hold no admin credentials; they
forward the user's token, and the HRMS API applies `policy.yaml`. Each system has its own
database (`hrms_db`, later `crm_db`, `pm_db`); systems link only by `emp_code` / email.

## Alternatives
- Agent with read-only SQL: rejected, RBAC would have to be rebuilt in SQL or prompts.
- MCP talks to the DB directly: rejected, two places to keep permissions in sync.

## Consequences
- RBAC lives in exactly one place per system.
- One extra network hop per tool call (measure in Langfuse).
- Cross-system joins happen in the agent, which is the realistic hard problem to learn.
