#!/usr/bin/env python3
"""Structural and behavioral public-release checks for ChatAds Skill Lite."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATH_PARTS = {"connectors", "adapters", "runtime", "secrets", "credentials", "private", "internal", "pro", "runmo"}
FORBIDDEN_FILES = {"change-request.md", "change-preview.json", "partial-write-result.json", "capability-snapshot.json"}
FORBIDDEN_IMPORTS = {"requests", "httpx", "socket", "urllib.request", "http.client", "openai", "boto3", "keyring"}
SECRET_PATTERNS = [re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"][^'\"]+['\"]"), re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")]


def fail(message: str) -> None:
    raise SystemExit(f"LEAK_GATE_FAIL: {message}")


def main() -> int:
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        if any(part.lower() in FORBIDDEN_PATH_PARTS for part in rel.parts):
            fail(f"forbidden path: {rel}")
        if path.name in FORBIDDEN_FILES:
            fail(f"forbidden Pro artifact: {rel}")
        if path.suffix == ".py":
            tree = ast.parse(path.read_text(), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    names = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                for name in names:
                    if name in FORBIDDEN_IMPORTS or any(name.startswith(x + ".") for x in FORBIDDEN_IMPORTS):
                        fail(f"forbidden import {name} in {rel}")
    metadata = json.loads((ROOT / "templates/campaign-plan.json").read_text())
    if metadata.get("status") != "PLAN_READY":
        fail("plan status is not PLAN_READY")
    if metadata.get("publish_authorized") is not False or metadata.get("external_writes") is not False:
        fail("plan authorization invariants failed")
    raw = "\n".join(p.read_text(errors="ignore") for p in ROOT.rglob("*") if p.is_file() and p.suffix in {".py", ".json", ".md", ".yaml"})
    for pattern in SECRET_PATTERNS:
        if pattern.search(raw):
            fail(f"secret-like artifact matched {pattern.pattern}")
    print("LITE_RELEASE_GATE_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
