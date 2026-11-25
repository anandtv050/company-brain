# Company Brain

An enterprise AI copilot for **NimbusTech**, a fictional 250-person IT services company.
Employees ask questions across HR, projects, sales and finance; agents also run on events
and schedules, and every write action waits for human approval. All data is synthetic.

**Current slice:** HRMS (Nov 25 – Dec 5, 2026).

## Architecture (short)

```
UI / events / schedules
        │
   LangGraph agents ──► LiteLLM gateway ──► cloud model | Ollama (local)
        │
   MCP servers (hrms, policy, platform) ── user token passed through
        │                         │
   HRMS API (RBAC + audit)     RAG (pgvector, permission filter first)
        │
     hrms_db
```

Design rules: the AI never touches a database directly (ADR-002); permission is checked
before retrieval, never after (ADR-003); the LLM never decides permissions (`docs/rbac.md`).

## Run locally

Needs Docker Desktop and Python 3.11+.

```bash
cp infra/.env.example infra/.env        # then change the secrets
docker compose -f infra/docker-compose.yml --env-file infra/.env up -d
pip install "psycopg[binary]" redis
python scripts/check_stack.py           # all services should say OK
```

With `make`: `make up`, `make check`, `make ps`, `make down`.
Ollama in Docker is optional: `make up-llm` (or run Ollama / LM Studio natively).

| Service | URL / port |
| --- | --- |
| Postgres (`hrms_db`, `agent_db`, `langfuse`) | localhost:5432 |
| Redis | localhost:6379 |
| Mailpit (fake inbox) | http://localhost:8025 (SMTP 1025) |
| Langfuse (tracing) | http://localhost:3000 |
| Ollama (optional) | localhost:11434 |

## Repo layout

| Path | What |
| --- | --- |
| `infra/` | Docker Compose, Postgres init, env template |
| `data/generators/` | Fake company + HRMS history generators |
| `data/docs/` | HR policy documents for RAG |
| `services/hrms-api/` | Fake HRMS: own DB, JWT, RBAC policy engine, audit log |
| `mcp/` | `hrms-mcp`, `policy-mcp`, `platform-mcp` |
| `rag/` | Parse, chunk, embed, retrieve, rerank |
| `agents/` | LangGraph graphs + triggers (webhooks, scheduler) |
| `gateway/` | LiteLLM config and routing rules |
| `web/` | Chat UI, persona switcher, approvals inbox |
| `evals/` | Datasets, runners, reports |
| `docs/` | RBAC design, ADRs |

## Progress

| Day | Date | Status |
| --- | --- | --- |
| 1 | Nov 25 | Repo, local stack, RBAC design, ADR-001..003 |
