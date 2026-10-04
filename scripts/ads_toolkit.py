#!/usr/bin/env python3
"""Offline helpers for ChatAds Skill. No HTTP, browser, credentials or ad writes.

Internal data contract, NOT an OpenAI Ads API payload or bulk-upload format.
Python 3.10+; standard library only. Numbers in monetary inputs are major units.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

VERSION = "1.0.0"
CONTRACT_VERSION = "1.0"
REQUIRED_METRIC_COLUMNS = (
    "date", "account_id", "campaign_id", "ad_group_id", "ad_id", "currency",
    "timezone", "attribution", "conversion_event", "impressions", "clicks", "spend",
)
NUMERIC_METRICS = ("impressions", "clicks", "spend", "conversions", "revenue")
SOURCE_HOSTS = {"help.openai.com", "developers.openai.com", "openai.com", "ads.openai.com"}


class ValidationError(ValueError):
    """Input does not match the local contract."""


def number(value: Any, name: str, *, optional: bool = False) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        if optional:
            return None
        raise ValidationError(f"{name}: missing numeric value")
    if isinstance(value, bool):
        raise ValidationError(f"{name}: booleans are not numbers")
    if not isinstance(value, (str, int, float)):
        raise ValidationError(f"{name}: expected a number")
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValidationError(f"{name}: use a plain decimal without currency symbols/separators") from exc
    if not math.isfinite(result) or result < 0:
        raise ValidationError(f"{name}: expected a finite non-negative number")
    return result


def text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name}: expected non-empty text")
    return value.strip()


def iso_date(value: Any, name: str) -> dt.date:
    raw = text(value, name)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise ValidationError(f"{name}: expected YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(raw)
    except ValueError as exc:
        raise ValidationError(f"{name}: invalid calendar date") from exc


def currency_code(value: Any) -> str:
    value = text(value, "currency")
    if not re.fullmatch(r"[A-Z]{3}", value):
        raise ValidationError("currency: expected an uppercase three-letter billing code")
    return value


def timezone_name(value: Any) -> str:
    value = text(value, "timezone")
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValidationError(f"timezone: unknown IANA timezone {value!r}") from exc
    return value


def https_url(value: Any) -> str:
    value = text(value, "url")
    if any(ch.isspace() or ord(ch) < 32 for ch in value):
        raise ValidationError("url: whitespace/control characters are not accepted")
    try:
        parts = urlsplit(value)
        port = parts.port
    except ValueError as exc:
        raise ValidationError("url: malformed URL") from exc
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        raise ValidationError("url: expected an absolute HTTPS URL without embedded credentials")
    if port is not None and not 0 < port < 65536:
        raise ValidationError("url: invalid port")
    return value


def build_utm(url: str, campaign: str, content: str, source: str = "chatgpt",
              medium: str = "paid", *, replace: bool = False) -> str:
    """Preserve existing query pairs and fragments; never overwrite UTMs silently."""
    parts = urlsplit(https_url(url))
    values = {"utm_source": source, "utm_medium": medium,
              "utm_campaign": campaign, "utm_content": content}
    for key, val in values.items():
        val = text(val, key)
        if any(ord(ch) < 32 for ch in val):
            raise ValidationError(f"{key}: control characters are not accepted")
        values[key] = val
    existing = parse_qsl(parts.query, keep_blank_values=True)
    conflicts = {key.lower() for key, _ in existing} & set(values)
    if conflicts and not replace:
        raise ValidationError("existing UTM parameters; use --replace explicitly to replace them")
    kept = [(key, val) for key, val in existing if not (replace and key.lower() in values)]
    return urlunsplit((parts.scheme, parts.netloc, parts.path,
                       urlencode(kept + list(values.items())), parts.fragment))


def ratio(numerator: float | None, denominator: float | None,
          scale: float = 1.0) -> float | None:
    if numerator is None or denominator is None or denominator == 0:
        return None
    value = numerator / denominator * scale
    if not math.isfinite(value):
        raise ValidationError("derived ratio overflow; inspect the input scale")
    return value


def analyze_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Ad/day grain only. Reject mixed accounts, currencies, attribution and events.

    Unknown conversions/revenue stay unknown at the aggregate level. CVR is
    deliberately named conversions_per_click_proxy; view-through conversions
    and multiple conversion events mean this is not necessarily purchase CVR.
    """
    if not isinstance(rows, list) or not rows:
        raise ValidationError("metrics: expected a non-empty array of ad/day rows")
    cleaned: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    dimensions: set[tuple[str, ...]] = set()
    origins: set[str] = set()
    warnings: set[str] = set()
    for row_number, raw in enumerate(rows, 1):
        if not isinstance(raw, dict):
            raise ValidationError(f"row {row_number}: expected an object")
        origin = raw.get("data_origin", "unknown")
        if not isinstance(origin, str) or origin not in {"user", "synthetic", "unknown"}:
            raise ValidationError("data_origin: expected user, synthetic, or unknown")
        origins.add(origin)
        missing = set(REQUIRED_METRIC_COLUMNS) - raw.keys()
        if missing:
            raise ValidationError(f"row {row_number}: missing columns {sorted(missing)}")
        item = {key: text(raw[key], key) for key in REQUIRED_METRIC_COLUMNS
                if key not in NUMERIC_METRICS}
        iso_date(item["date"], "date")
        currency_code(item["currency"])
        timezone_name(item["timezone"])
        for key in ("account_id", "campaign_id", "ad_group_id", "ad_id"):
            if item[key].lower() in {"total", "all", "subtotal", "grand total"}:
                raise ValidationError("aggregate/total rows are not accepted; use ad/day grain")
        dimensions.add(tuple(item[key] for key in
                             ("account_id", "currency", "timezone", "attribution", "conversion_event")))
        grain = (item["date"], item["ad_id"])
        if grain in seen:
            raise ValidationError(f"duplicate ad/day row {grain}; do not combine totals or breakdowns")
        seen.add(grain)
        for key in NUMERIC_METRICS:
            item[key] = number(raw.get(key), key, optional=key in {"conversions", "revenue"})
        for key in ("impressions", "clicks"):
            if not item[key].is_integer():
                raise ValidationError(f"row {row_number}: {key} must be an integer")
        if item["clicks"] > item["impressions"]:
            warnings.add("CLICKS_EXCEED_IMPRESSIONS: confirm export grain and reporting semantics")
        if item["spend"] == 0:
            warnings.add("ZERO_REPORTED_SPEND: verify reporting maturity; zero is not proof of no charges")
        cleaned.append(item)
    if len(origins) != 1:
        raise ValidationError("mixed data origins: never combine synthetic and real/unknown reports")
    origin = next(iter(origins))
    if origin != "user":
        warnings.add("DATA_ORIGIN_" + origin.upper() + ": not verified real account performance")
    if len(dimensions) != 1:
        raise ValidationError("mixed account/currency/timezone/attribution/conversion-event exports; analyze separately")

    # An ad identifier must not silently change parent across report dates.
    parents: dict[str, tuple[str, str]] = {}
    for item in cleaned:
        parent = (item["campaign_id"], item["ad_group_id"])
        if item["ad_id"] in parents and parents[item["ad_id"]] != parent:
            raise ValidationError("inconsistent parent campaign/ad-group for the same ad ID")
        parents[item["ad_id"]] = parent

    def summarize(subset: list[dict[str, Any]]) -> dict[str, Any]:
        sums: dict[str, float | None] = {}
        coverage: dict[str, int] = {}
        for metric in NUMERIC_METRICS:
            values = [item[metric] for item in subset]
            coverage[metric] = sum(value is not None for value in values)
            sums[metric] = sum(values) if all(value is not None for value in values) else None
        if any(value is not None and not math.isfinite(value) for value in sums.values()):
            raise ValidationError("metric totals overflow; use smaller valid inputs")
        return {
            "rows": len(subset), "totals": sums, "known_rows": coverage,
            "metrics": {
                "ctr_percent": ratio(sums["clicks"], sums["impressions"], 100),
                "cpc": ratio(sums["spend"], sums["clicks"]),
                "cpm": ratio(sums["spend"], sums["impressions"], 1000),
                "conversions_per_click_proxy_percent": ratio(sums["conversions"], sums["clicks"], 100),
                "cpa": ratio(sums["spend"], sums["conversions"]),
                "roas": ratio(sums["revenue"], sums["spend"]),
            },
        }

    if any(item["conversions"] is None for item in cleaned):
        warnings.add("INCOMPLETE_CONVERSIONS: aggregate CPA and conversion rate are null")
    if any(item["revenue"] is None for item in cleaned):
        warnings.add("INCOMPLETE_REVENUE: aggregate ROAS is null")
    warnings.add("MATURITY_NOT_VERIFIED: confirm reporting lag and attribution window before decisions")
    warnings.add("NOT_CAUSAL: attributed conversions/ROAS do not establish incrementality or profit")
    dim = next(iter(dimensions))
    return {
        "contract_version": CONTRACT_VERSION, "external_writes": False, "data_origin": origin,
        "dimensions": dict(zip(("account_id", "currency", "timezone", "attribution", "conversion_event"), dim)),
        "date_range": {"since": min(item["date"] for item in cleaned),
                       "until": max(item["date"] for item in cleaned)},
        "summary": summarize(cleaned),
        "campaigns": {key: summarize([item for item in cleaned if item["campaign_id"] == key])
                      for key in sorted({item["campaign_id"] for item in cleaned})},
        "warnings": sorted(warnings),
        "decision": "DESCRIPTIVE_ONLY_NO_AUTOMATIC_BUDGET_CHANGE",
    }


def economics(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("economics: expected an object")
    currency = currency_code(data.get("currency"))
    revenue = number(data.get("net_revenue_per_order"), "net_revenue_per_order")
    costs = number(data.get("variable_cost_per_order"), "variable_cost_per_order")
    profit = number(data.get("target_profit_per_order"), "target_profit_per_order")
    cvr = number(data.get("click_to_purchase_cvr"), "click_to_purchase_cvr", optional=True)
    if cvr is not None and cvr > 1:
        raise ValidationError("click_to_purchase_cvr: use a fraction between 0 and 1, not a percentage")
    contribution = revenue - costs
    room = contribution - profit
    if not all(math.isfinite(x) for x in (contribution, room)):
        raise ValidationError("derived economics overflow; inspect the input scale")
    return {
        "currency": currency, "assumptions": data,
        "contribution_before_ads": contribution,
        "break_even_cpa": contribution if contribution > 0 else None,
        "target_cpa_ceiling": room if room > 0 else None,
        "break_even_roas": ratio(revenue, contribution) if contribution > 0 else None,
        "break_even_cpc": contribution * cvr if contribution > 0 and cvr is not None else None,
        "target_cpc_ceiling": room * cvr if room > 0 and cvr is not None else None,
        "status": "NO_POSITIVE_ACQUISITION_ROOM" if room <= 0 else "ASSUMPTION_BASED_NOT_A_BID_RECOMMENDATION",
        "external_writes": False,
    }


def validate_plan(plan: dict[str, Any], *, today: dt.date | None = None) -> dict[str, Any]:
    """Local completeness check, never authorization or a semantic compliance verdict."""
    if not isinstance(plan, dict):
        raise ValidationError("plan: expected an object")
    explicit_today = today
    blockers: list[str] = []
    warnings = ["LOCAL_CHECK_ONLY: evidence truth, ad policy and account access require human verification",
                "NO_LOCAL_PUBLISHER: this script cannot submit ads; host tools require a separate human approval gate"]

    def block(condition: bool, message: str) -> None:
        if not condition:
            blockers.append(message)

    def check(fn: Any, value: Any, label: str) -> Any:
        try:
            return fn(value)
        except (ValidationError, ValueError, TypeError) as exc:
            blockers.append(f"{label}: {exc}")
            return None

    def obj(key: str) -> dict[str, Any]:
        value = plan.get(key)
        if not isinstance(value, dict):
            blockers.append(f"{key}: expected an object")
            return {}
        return value

    block(plan.get("schema_version") == CONTRACT_VERSION, "unsupported schema_version")
    block(plan.get("mode") == "draft", "V1 supports draft mode only")
    block(plan.get("data_origin") == "user", "SYNTHETIC_OR_UNKNOWN_ORIGIN: not a real campaign submission")
    brand, account, campaign = obj("brand"), obj("account"), obj("campaign")
    capabilities, measurement, checks = obj("capabilities"), obj("measurement"), obj("checks")
    check(lambda x: text(x, "brand.name"), brand.get("name"), "brand.name")
    check(https_url, brand.get("landing_url"), "brand.landing_url")
    check(currency_code, account.get("currency"), "account.currency")
    tz = check(timezone_name, account.get("timezone"), "account.timezone")
    local_today = explicit_today or dt.datetime.now(ZoneInfo(tz) if tz else dt.timezone.utc).date()
    if explicit_today is not None:
        warnings.append("TEST_DATE_OVERRIDE: --as-of is for fixtures, not evidence of live freshness")
    home = account.get("country")
    block(isinstance(home, str) and bool(re.fullmatch(r"[A-Z]{2}", home or "")), "account.country: ISO two-letter code required")
    check(lambda x: text(x, "account.id"), account.get("id"), "account.id")
    for key in ("eligibility", "verification"):
        block(account.get(key) == "verified", f"account.{key}: not verified")
    block(capabilities.get("constraints_verified") is True, "platform/account constraints not verified")
    # Seven days is OUR freshness policy, not an OpenAI guarantee.
    for key in ("checked_at", "account_snapshot_checked_at"):
        verified = check(lambda x: iso_date(x, key), capabilities.get(key), key)
        if verified:
            age = (local_today - verified).days
            block(0 <= age <= 7, f"{key}: stale or future verification; local freshness limit is 7 days")
    urls = capabilities.get("source_urls")
    block(isinstance(urls, list) and bool(urls), "official source URLs missing")
    if isinstance(urls, list):
        for url in urls:
            valid = check(https_url, url, "source_url")
            if valid:
                block(urlsplit(valid).hostname in SOURCE_HOSTS, "platform source is not an approved official domain")
    for key in ("landing_page", "claims", "policy", "creative_specs"):
        block(checks.get(key) == "verified", f"checks.{key}: not verified")
    check(lambda x: text(x, "campaign.name"), campaign.get("name"), "campaign.name")
    objective = campaign.get("objective")
    block(isinstance(objective, str) and objective in {"reach", "clicks", "conversions"},
          "objective: use the INTERNAL intent reach/clicks/conversions, not an API enum")
    po = check(lambda x: text(x, "platform_objective"), campaign.get("platform_objective"), "platform_objective")
    pb = check(lambda x: text(x, "platform_billing"), campaign.get("platform_billing"), "platform_billing")
    supported = capabilities.get("supported_objective_billing_pairs")
    block(isinstance(supported, list) and bool(supported), "fresh account-supported objective/billing pairs required")
    if isinstance(supported, list):
        block(any(isinstance(pair, dict) and pair.get("intent") == objective
                  and pair.get("objective") == po and pair.get("billing") == pb
                  and po is not None and pb is not None for pair in supported),
              "selected intent/objective/billing is not present in the verified account snapshot")
    block(capabilities.get("unresolved_conflicts") == [], "platform/account capability conflicts unresolved")
    targets = campaign.get("target_countries")
    block(isinstance(targets, list) and bool(targets), "explicit target_countries required")
    if isinstance(targets, list):
        block(all(isinstance(x, str) and re.fullmatch(r"[A-Z]{2}", x) for x in targets), "invalid target country code")
        if any(country != home for country in targets):
            block(account.get("cross_border") == "verified", "cross-border account access not verified")
    budget = campaign.get("budget")
    if not isinstance(budget, dict):
        budget = {}
        blockers.append("campaign.budget: expected an object")
    amount = check(lambda x: number(x, "budget.amount"), budget.get("amount"), "budget.amount")
    ceiling = check(lambda x: number(x, "max_total_spend"), budget.get("max_total_spend"), "max_total_spend")
    block(amount is not None and amount > 0, "positive budget required")
    block(ceiling is not None and ceiling > 0, "positive human-defined total spend ceiling required")
    block(budget.get("type") in ("daily", "campaign_total"), "unsupported budget type")
    start = check(lambda x: iso_date(x, "start_date"), campaign.get("start_date"), "start_date")
    end = check(lambda x: iso_date(x, "end_date"), campaign.get("end_date"), "end_date")
    if start and end:
        block(end >= start, "campaign ends before it starts")
        block(start >= local_today, "planned start is in the past")
    if amount is not None and ceiling is not None:
        if budget.get("type") == "campaign_total":
            block(amount <= ceiling, "campaign total exceeds the stated spend ceiling")
        elif budget.get("type") == "daily":
            minimum = check(lambda x: number(x, "minimum_daily_budget"), capabilities.get("minimum_daily_budget"), "minimum_daily_budget")
            if minimum is not None:
                block(amount >= minimum, "daily budget below freshly verified account-currency minimum")
            warnings.append("DAILY_IS_NOT_HARD_CAP: nominal daily allocation is not a guaranteed spend ceiling")
            block(budget.get("hard_total_limit_verified") is True,
                  "daily budget needs a separately verified platform-enforced total limit for this strict-cap workflow")
            hard_cap = check(lambda x: number(x, "platform_total_limit"), budget.get("platform_total_limit"), "platform_total_limit")
            if hard_cap is not None:
                block(hard_cap > 0 and hard_cap <= ceiling,
                      "platform total limit is missing/zero or exceeds the human-approved media-spend ceiling")
            if start and end and end >= start:
                planned = amount * ((end - start).days + 1)
                block(planned <= ceiling, "nominal daily allocation exceeds stated total spend ceiling")
    if objective == "conversions":
        block(measurement.get("method") in ("pixel", "capi", "pixel_and_capi"), "conversion tracking not configured")
        block(measurement.get("account_event_verified") is True, "standard conversion event not verified for account")
        block(measurement.get("active_standard_event_count") == 1 and not isinstance(measurement.get("active_standard_event_count"), bool),
              "exactly one active standard optimization event required")
        block(measurement.get("event_account_id") == account.get("id"), "conversion event belongs to a different account")
        block(measurement.get("privacy_review") == "verified", "measurement privacy/consent review not verified")
        check(lambda x: text(x, "standard_event"), measurement.get("standard_event"), "standard_event")
        check(lambda x: text(x, "attribution"), measurement.get("attribution"), "attribution")
    claims = plan.get("claims", [])
    claim_map: dict[str, Any] = {}
    if not isinstance(claims, list):
        blockers.append("claims: expected an array")
        claims = []
    for item in claims:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            blockers.append("claim requires a non-empty id")
            continue
        block(item["id"] not in claim_map, "duplicate claim ID")
        claim_map[item["id"]] = item
        block(item.get("verified") is True and isinstance(item.get("evidence"), str) and bool(item["evidence"].strip()),
              f"unverified claim: {item['id']}")
    groups = campaign.get("ad_groups")
    block(isinstance(groups, list) and bool(groups), "no ad groups")
    if isinstance(groups, list):
        for group in groups:
            if not isinstance(group, dict):
                blockers.append("ad group must be an object")
                continue
            check(lambda x: text(x, "ad_group.name"), group.get("name"), "ad_group.name")
            hints = group.get("context_hints")
            block(isinstance(hints, list) and bool(hints) and all(isinstance(x, str) and x.strip() for x in hints),
                  "ad group requires context-hint drafts")
            ads = group.get("ads")
            block(isinstance(ads, list) and bool(ads), "ad group has no ads")
            if isinstance(ads, list):
                for ad in ads:
                    if not isinstance(ad, dict):
                        blockers.append("ad must be an object")
                        continue
                    for key in ("title", "description", "creative_asset_reference"):
                        check(lambda x: text(x, key), ad.get(key), f"ad.{key}")
                    check(https_url, ad.get("landing_url"), "ad.landing_url")
                    ids = ad.get("claim_ids")
                    block(isinstance(ids, list) and bool(ids), "ad claim_ids required")
                    if isinstance(ids, list):
                        block(all(isinstance(x, str) and x in claim_map for x in ids), "ad references unknown claim IDs")
    return {"status": "BLOCKED" if blockers else "LOCAL_CHECKS_PASSED_NOT_AUTHORIZED",
            "blockers": blockers, "warnings": warnings, "external_writes": False,
            "publish_authorized": False, "as_of": local_today.isoformat()}


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: str) -> Any:
    with Path(path).open(encoding="utf-8-sig") as handle:
        return json.load(handle, object_pairs_hook=unique_object, parse_constant=lambda value: (_ for _ in ()).throw(
            ValidationError(f"non-standard JSON constant: {value}")))


def load_metrics(path: str) -> list[dict[str, Any]]:
    if Path(path).suffix.lower() == ".csv":
        with Path(path).open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            if len(headers) != len(set(headers)):
                raise ValidationError("duplicate CSV header")
            rows = list(reader)
            if any(None in row for row in rows):
                raise ValidationError("CSV row contains more fields than the header")
            return rows
    data = load_json(path)
    if not isinstance(data, list):
        raise ValidationError("metrics JSON must be an array")
    return data


def emit(data: Any, output: str | None) -> None:
    content = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if output:
        # Fail rather than silently overwrite a previous campaign analysis.
        with Path(output).open("x", encoding="utf-8") as handle:
            handle.write(content)
    else:
        print(content, end="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("analyze", "economics", "validate-plan"):
        p = sub.add_parser(command)
        p.add_argument("input")
        p.add_argument("--output", help="new JSON output path; existing files are not overwritten")
        if command == "validate-plan":
            p.add_argument("--as-of", help="YYYY-MM-DD; deterministic tests only, not a verification override")
    utm = sub.add_parser("utm")
    utm.add_argument("url")
    utm.add_argument("--campaign", required=True)
    utm.add_argument("--content", required=True)
    utm.add_argument("--source", default="chatgpt")
    utm.add_argument("--medium", default="paid")
    utm.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "utm":
            print(build_utm(args.url, args.campaign, args.content, args.source, args.medium, replace=args.replace))
            return 0
        if args.command == "analyze":
            result = analyze_rows(load_metrics(args.input))
        elif args.command == "economics":
            result = economics(load_json(args.input))
        else:
            as_of = iso_date(args.as_of, "as_of") if args.as_of else None
            result = validate_plan(load_json(args.input), today=as_of)
        emit(result, args.output)
        return 2 if result.get("status") == "BLOCKED" else 0
    except (ValidationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc), "external_writes": False}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
