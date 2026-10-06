"""
title: PHI Guard
author: MediAI
version: 1.0.0
description: Redacts protected health information from the latest user message before it reaches the model and appends an audit record (counts only, never values).
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

AUDIT_PATH = Path("/app/backend/data/medical_audit.jsonl")

PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "EMAIL"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN"),
    (re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "PHONE"),
    (re.compile(r"\b(?:MRN|Medical Record|Patient ID|PID)[:\s#]*\d+\b", re.IGNORECASE), "MRN"),
    (re.compile(r"\b(?:DOB|Date of Birth)[:\s]*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", re.IGNORECASE), "DOB"),
]
NAME_RE = re.compile(r"(?:[Pp]atient|Mr\.?|Mrs\.?|Ms\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)")


def redact(text: str, redact_names: bool) -> tuple[str, Dict[str, int]]:
    counts: Dict[str, int] = {}
    for pattern, label in PATTERNS:
        text, n = pattern.subn(f"[{label}]", text)
        if n:
            counts[label] = counts.get(label, 0) + n
    if redact_names:
        text, n = NAME_RE.subn(lambda m: m.group(0).replace(m.group(1), "[NAME]"), text)
        if n:
            counts["NAME"] = n
    return text, counts


def write_audit(user_id: Optional[str], counts: Dict[str, int]) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action": "phi_redacted",
        "counts": counts,
    }
    with AUDIT_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


class Filter:
    class Valves(BaseModel):
        enabled: bool = Field(default=True, description="Redact PHI before sending to the model")
        redact_names: bool = Field(default=True, description="Redact names that follow 'Patient', 'Mr.', 'Mrs.', 'Ms.'")

    def __init__(self):
        self.valves = self.Valves()

    def inlet(self, body: Dict[str, Any], __user__: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.valves.enabled:
            return body

        messages = body.get("messages", [])
        latest_user = next(
            (m for m in reversed(messages) if m.get("role") == "user" and isinstance(m.get("content"), str)),
            None,
        )
        if latest_user is None:
            return body

        for message in messages:
            if message.get("role") == "user" and isinstance(message.get("content"), str):
                redacted, counts = redact(message["content"], self.valves.redact_names)
                message["content"] = redacted
                if message is latest_user and counts:
                    write_audit((__user__ or {}).get("id"), counts)

        return body
