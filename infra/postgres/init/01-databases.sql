-- Runs once, on the first start of an empty Postgres volume.
-- One database per "system" (ADR-002: systems never share tables).

CREATE DATABASE hrms_db;    -- fake HRMS (source system)
CREATE DATABASE agent_db;   -- RAG vectors, LangGraph checkpoints, approvals
CREATE DATABASE langfuse;   -- tracing (owned by Langfuse)

\connect hrms_db
CREATE EXTENSION IF NOT EXISTS pgcrypto;

\connect agent_db
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
