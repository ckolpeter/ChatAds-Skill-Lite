#!/usr/bin/env python3
"""Offline Beginner First helpers for ChatAds Skill v1.1.

No HTTP, browser, credentials, event delivery, or ad writes. Inputs and outputs
are local contracts, not Ads Manager API payloads.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

VERSION = "1.1.0"
CONTRACT_VERSION = "1.1"


class ValidationError(ValueError):
    pass


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field}: expected non-empty text")
    return value.strip()


def _number(value: Any, field: str, *, optional: bool = False) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        if optional:
            return None
        raise ValidationError(f"{field}: missing number")
    if isinstance(value, bool):
        raise ValidationError(f"{field}: booleans are not numbers")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"{field}: expected a number") from exc
    if not math.isfinite(result) or result < 0:
        raise ValidationError(f"{field}: expected finite non-negative number")
    return result


def onboarding(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("onboarding: expected an object")
    fields = (
        ("offer", "你想賣什麼或提供什麼服務？"),
        ("customer", "你最想服務哪一類人？"),
        ("goal", "你希望對方做什麼？例如購買、填表或聯絡你？"),
        ("market", "想服務哪個市場或語言？"),
        ("landing_url", "使用者要去哪裡了解、購買或聯絡？"),
        ("spend_limit", "整段期間最多願意承擔多少媒體費？請提供幣別與金額。"),
        ("measurement", "你目前能驗證哪個成功行動？"),
    )
    missing = [key for key, _ in fields if data.get(key) in (None, "", [])]
    next_question = next((question for key, question in fields if key in missing), None)
    return {
        "contract_version": CONTRACT_VERSION,
        "status": "READY_FOR_STARTER_DRAFT" if not missing else "ONBOARDING_IN_PROGRESS",
        "completed_fields": [key for key, _ in fields if key not in missing],
        "missing_fields": missing,
        "next_question": next_question,
        "mode": "beginner",
        "external_writes": False,
    }


def budget_scenarios(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("budget: expected an object")
    currency = _text(data.get("currency"), "currency")
    total = _number(data.get("total_budget"), "total_budget")
    days_value = _number(data.get("days"), "days")
    if not days_value or days_value < 1 or days_value != int(days_value):
        raise ValidationError("days: expected a positive whole number")
    days = int(days_value)
    shares = data.get("shares", [0.5, 0.75, 1.0])
    if not isinstance(shares, list) or not shares:
        raise ValidationError("shares: expected a non-empty array")
    scenarios = []
    for share in shares:
        share_value = _number(share, "share")
        if share_value is None or share_value > 1:
            raise ValidationError("share: expected a fraction from 0 to 1")
        scenario_total = total * share_value
        scenarios.append({"share": share_value, "total": scenario_total,
                          "average_daily": scenario_total / days})
    return {"contract_version": CONTRACT_VERSION, "currency": currency,
            "days": days, "scenarios": scenarios,
            "status": "ASSUMPTION_ONLY_NOT_APPROVED", "external_writes": False,
            "guardrails": ["daily allocation is not a hard daily cap",
                            "no automatic budget increase", "total ceiling required before write"]}


TERMS = {
    "campaign": "一組共同目標與預算的廣告工作；新手可先把它理解成一個測試盒。",
    "ad_group": "同一類需求情境的廣告集合；不是必須先學會的設定名詞。",
    "cpc": "平均每次點擊花多少錢。",
    "cpm": "每一千次展示平均花多少錢；不是每千人一定看到。",
    "context_hints": "描述使用者需求情境的提示；不是精準 targeting，也不保證觸達某句對話。",
    "roas": "歸因營收除以廣告費；沒有驗證轉換與營收時不能可靠解讀。",
    "cpa": "每個歸因轉換的平均廣告費；轉換事件未驗證時不能當成可靠獲客成本。",
}


def explain(term: str) -> dict[str, Any]:
    key = _text(term, "term").lower().replace(" ", "_")
    return {"term": key, "explanation": TERMS.get(key, "這個詞需要依目前平台 schema 或你的工作情境再確認。"),
            "known": key in TERMS, "external_writes": False}


def landing_readiness(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("landing page: expected an object")
    checks = ("url_accessible", "offer_matches_ad", "price_or_terms_visible",
              "primary_action_works", "privacy_and_consent", "tracking_owner")
    unknown = [key for key in checks if data.get(key) not in (True, False)]
    failed = [key for key in checks if data.get(key) is False]
    return {"status": "READY" if not unknown and not failed else "CHECK_REQUIRED",
            "unknown": unknown, "failed": failed, "checks": list(checks),
            "external_writes": False}


def translate_metrics(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("metrics: expected an object")
    clicks = data.get("clicks")
    impressions = data.get("impressions")
    spend = data.get("spend")
    tracking = data.get("conversion_tracking_verified") is True
    lines = []
    if clicks is not None and impressions not in (None, 0):
        lines.append(f"有 {clicks} 次點擊，約佔展示的 {float(clicks) / float(impressions) * 100:.2f}%。")
    if spend is not None and clicks not in (None, 0):
        lines.append(f"平均每次點擊花費約 {float(spend) / float(clicks):.2f}。")
    if not tracking:
        lines.append("轉換追蹤尚未驗證，所以 CPA/ROAS 不能可靠判讀；目前只能看點擊層級訊號。")
    return {"plain_language": lines, "reliable_conversion_conclusion": tracking,
            "status": "DESCRIPTIVE_ONLY" if not tracking else "CONVERSION_DATA_CAN_BE_REVIEWED",
            "external_writes": False}


def load(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"input: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("onboarding", "budget", "explain", "landing", "translate-metrics"):
        p = sub.add_parser(command)
        p.add_argument("input")
        if command == "explain":
            p.add_argument("--term", required=True)
    args = parser.parse_args(argv)
    try:
        data = load(args.input)
        functions = {"onboarding": onboarding, "budget": budget_scenarios,
                     "landing": landing_readiness, "translate-metrics": translate_metrics}
        result = explain(args.term) if args.command == "explain" else functions[args.command](data)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if result.get("status") not in ("BLOCKED", "RUNTIME_VERIFY_REQUIRED", "CHECK_REQUIRED") else 2
    except ValidationError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc), "external_writes": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
