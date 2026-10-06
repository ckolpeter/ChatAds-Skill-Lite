#!/usr/bin/env python3
"""Structural and behavioral public-release checks for ChatAds Skill Lite."""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATH_PARTS = {"connectors", "adapters", "runtime", "secrets", "credentials", "private", "internal", "pro", "runmo"}
FORBIDDEN_FILES = {"change-request.md", "change-preview.json", "partial-write-result.json", "capability-snapshot.json"}
FORBIDDEN_IMPORTS = {"requests", "httpx", "socket", "urllib.request", "http.client", "openai", "boto3", "keyring"}
SECRET_PATTERNS = [re.compile(r"(?i)(api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"][^'\"]+['\"]"), re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")]
CONTENTS_RE = re.compile(r"^##\s+(contents|table of contents|目錄|目录)\s*$", re.I | re.M)
REQUIRED_SKILL_SECTIONS = (
    "## Reference map",
    "## Degrees of freedom",
    "## Ordered execution checklist",
    "## Self-correction loop",
    "## Dependencies",
)


def fail(message: str) -> None:
    raise SystemExit(f"LEAK_GATE_FAIL: {message}")


def best_practices() -> None:
    skill_path = ROOT / "SKILL.md"
    skill = skill_path.read_text(encoding="utf-8")
    if len(skill.splitlines()) > 500:
        fail("SKILL.md exceeds 500 lines")
    for heading in REQUIRED_SKILL_SECTIONS:
        if heading not in skill:
            fail(f"missing best-practice section: {heading}")

    ref_root = ROOT / "references"
    references = sorted(ref_root.rglob("*.md"))
    for path in references:
        if path.parent != ref_root:
            fail(f"nested reference path is not allowed: {path.relative_to(ROOT)}")
        rel = path.relative_to(ROOT).as_posix()
        if rel not in skill:
            fail(f"reference is not linked directly from SKILL.md: {rel}")
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > 100 and not CONTENTS_RE.search("\n".join(lines[:40])):
            fail(f"reference over 100 lines lacks a top content list: {rel}")

    model_matrix = ROOT / "evals" / "MODEL_EVAL_MATRIX.md"
    audit = ROOT / "docs" / "BEST_PRACTICES_AUDIT.md"
    if not model_matrix.is_file() or not audit.is_file():
        fail("missing best-practices audit or model-eval matrix")

    local_modules = {p.stem for p in (ROOT / "scripts").glob("*.py")}
    stdlib = getattr(sys, "stdlib_module_names", set())
    for path in (ROOT / "scripts").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            else:
                continue
            for name in names:
                if stdlib and name not in stdlib and name not in local_modules:
                    fail(f"undeclared non-stdlib dependency {name} in {path.relative_to(ROOT)}")


def main() -> int:
    best_practices()
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
