"""Day 1 "done when" check: every service in the local stack answers.

Usage:  python scripts/check_stack.py
Needs:  pip install "psycopg[binary]" redis
Reads connection settings from infra/.env (falls back to .env.example defaults).
"""
from __future__ import annotations

import socket
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for name in (".env.example", ".env"):  # .env overrides the example
        path = ROOT / "infra" / name
        if path.exists():
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()
    return env


def check_postgres(env: dict[str, str]) -> str:
    import psycopg

    dsn = (
        f"host=localhost port={env.get('POSTGRES_PORT', '5432')} "
        f"user={env['POSTGRES_USER']} password={env['POSTGRES_PASSWORD']}"
    )
    found = []
    for db, ext in (("hrms_db", None), ("agent_db", "vector"), ("langfuse", None)):
        with psycopg.connect(f"{dsn} dbname={db}", connect_timeout=5) as conn:
            if ext:
                row = conn.execute(
                    "SELECT extversion FROM pg_extension WHERE extname = %s", (ext,)
                ).fetchone()
                if not row:
                    raise RuntimeError(f"{db}: extension {ext} missing")
                found.append(f"{db} ({ext} {row[0]})")
            else:
                found.append(db)
    return ", ".join(found)


def check_redis(env: dict[str, str]) -> str:
    import redis

    client = redis.Redis(host="localhost", port=int(env.get("REDIS_PORT", 6379)))
    client.ping()
    return "PONG"


def check_http(url: str) -> str:
    with urllib.request.urlopen(url, timeout=5) as resp:
        return f"HTTP {resp.status}"


def check_tcp(port: int) -> str:
    with socket.create_connection(("localhost", port), timeout=3):
        return f"port {port} open"


def main() -> int:
    env = load_env()
    checks = {
        "postgres": lambda: check_postgres(env),
        "redis": lambda: check_redis(env),
        "mailpit smtp": lambda: check_tcp(int(env.get("MAILPIT_SMTP_PORT", 1025))),
        "mailpit ui": lambda: check_http(f"http://localhost:{env.get('MAILPIT_UI_PORT', 8025)}/"),
        "langfuse": lambda: check_http(
            f"http://localhost:{env.get('LANGFUSE_PORT', 3000)}/api/public/health"
        ),
    }
    if "--ollama" in sys.argv:
        checks["ollama"] = lambda: check_http(
            f"http://localhost:{env.get('OLLAMA_PORT', 11434)}/api/tags"
        )

    failed = 0
    for name, fn in checks.items():
        try:
            print(f"  OK    {name:<13} {fn()}")
        except Exception as exc:  # noqa: BLE001 - report every failure, keep going
            failed += 1
            print(f"  FAIL  {name:<13} {type(exc).__name__}: {exc}")
    print("\nAll services healthy." if not failed else f"\n{failed} check(s) failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
