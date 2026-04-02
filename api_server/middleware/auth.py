"""API key authentication and rate limiting for REST API."""

import sqlite3
import secrets
from datetime import datetime, timezone
from fastapi import Request, HTTPException

DB_PATH = "docforge_api.db"

PLAN_LIMITS = {"free": 10, "basic": 100, "pro": 1000, "business": 10000}


def _init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS api_keys (key TEXT PRIMARY KEY, plan TEXT NOT NULL DEFAULT 'free', created_at TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS usage (key TEXT NOT NULL, year_month TEXT NOT NULL, count INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (key, year_month))")
    conn.execute("INSERT OR IGNORE INTO api_keys (key, plan, created_at) VALUES (?, ?, ?)", ("df_test_key", "pro", datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()

_init_db()


def _get_key_info(api_key: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT key, plan FROM api_keys WHERE key = ?", (api_key,)).fetchone()
    conn.close()
    return {"key": row[0], "plan": row[1]} if row else None


def _get_usage(api_key: str) -> int:
    ym = datetime.now(timezone.utc).strftime("%Y-%m")
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT count FROM usage WHERE key = ? AND year_month = ?", (api_key, ym)).fetchone()
    conn.close()
    return row[0] if row else 0


def _increment(api_key: str):
    ym = datetime.now(timezone.utc).strftime("%Y-%m")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO usage (key, year_month, count) VALUES (?, ?, 1) ON CONFLICT(key, year_month) DO UPDATE SET count = count + 1", (api_key, ym))
    conn.commit()
    conn.close()


async def verify_api_key(request: Request) -> dict:
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail={"error": "auth_required", "message": "Missing X-API-Key header"})
    info = _get_key_info(api_key)
    if not info:
        raise HTTPException(status_code=401, detail={"error": "invalid_api_key", "message": "Invalid API key"})
    limit = PLAN_LIMITS.get(info["plan"], 10)
    used = _get_usage(api_key)
    if used >= limit:
        raise HTTPException(status_code=429, detail={"error": "rate_limit_exceeded", "message": f"Monthly limit of {limit} documents exceeded", "used": used, "limit": limit})
    return {"key": api_key, "plan": info["plan"], "used": used, "limit": limit}


def increment_usage(api_key: str):
    _increment(api_key)
