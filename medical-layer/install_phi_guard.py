"""Install the PHI Guard filter into a running Open WebUI instance and enable it for all models.

Usage:
  OWUI_URL=http://localhost:8080 OWUI_ADMIN_EMAIL=... OWUI_ADMIN_PASSWORD=... python install_phi_guard.py
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

FUNCTION_ID = "phi_guard"
FILTER_PATH = Path(__file__).with_name("phi_guard_filter.py")


def call(base: str, method: str, path: str, token: str | None = None, body: dict | None = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode(errors="replace")


def main() -> int:
    base = os.environ.get("OWUI_URL", "http://localhost:8080").rstrip("/")
    email = os.environ["OWUI_ADMIN_EMAIL"]
    password = os.environ["OWUI_ADMIN_PASSWORD"]

    status, signin = call(base, "POST", "/api/v1/auths/signin", body={"email": email, "password": password})
    if status != 200:
        print(f"sign-in failed: HTTP {status}", file=sys.stderr)
        return 1
    token = signin["token"]

    form = {
        "id": FUNCTION_ID,
        "name": "PHI Guard",
        "content": FILTER_PATH.read_text(encoding="utf-8"),
        "meta": {"description": "Redacts PHI from user messages before they reach the model and writes an audit record."},
    }
    status, _ = call(base, "POST", "/api/v1/functions/create", token, form)
    if status == 400:
        status, _ = call(base, "POST", f"/api/v1/functions/id/{FUNCTION_ID}/update", token, form)
    if status != 200:
        print(f"install failed: HTTP {status}", file=sys.stderr)
        return 1

    status, fn = call(base, "GET", f"/api/v1/functions/id/{FUNCTION_ID}", token)
    if status != 200:
        print(f"lookup failed: HTTP {status}", file=sys.stderr)
        return 1
    if not fn.get("is_active"):
        call(base, "POST", f"/api/v1/functions/id/{FUNCTION_ID}/toggle", token)
    if not fn.get("is_global"):
        call(base, "POST", f"/api/v1/functions/id/{FUNCTION_ID}/toggle/global", token)

    status, fn = call(base, "GET", f"/api/v1/functions/id/{FUNCTION_ID}", token)
    print(f"installed: active={fn.get('is_active')} global={fn.get('is_global')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
