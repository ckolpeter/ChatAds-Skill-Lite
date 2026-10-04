---
name: chatads
description: ChatAds Skill Lite is an offline, beginner-first advertising planning Skill that exports a portable ChatAds Plan Contract and never performs live advertising mutations.
compatibility: Python 3.10+ standard library; no network, credentials, connector, or runtime dependency.
metadata:
  version: "1.1.0"
  edition: "lite"
  plan-contract: "chatads.plan@1.0"
  terminal-state: "PLAN_READY"
  external-reads: "false"
  external-writes: "false"
---

# ChatAds Skill Lite

ChatAds Skill Lite is the free, open-source planning edition. It helps a
beginner collect a business brief, translate goals, plan campaigns and ad
groups, describe Context Hints, prepare creative and landing-page checks,
explore budget scenarios, generate UTM parameters, analyze supplied data, and
export a portable `chatads.plan@1.0` artifact.

Lite is offline and planning-focused. It does not connect to Ads Manager,
resolve accounts, inspect live schemas, upload creatives, send events, create or
update platform objects, or hold credentials. Advanced live operation belongs
to ChatAds Skill Pro and is outside this repository.

## Workflow

1. Ask for the offer, customer, goal, market, landing page, total spend limit,
   and measurable success action.
2. Keep missing facts as questions or unknowns; do not invent product claims,
   prices, budgets, tracking access, or platform support.
3. Translate the goal into local planning intent such as `reach`, `clicks`, or
   `conversions`. These are planning labels, not live platform enums.
4. Build campaign, ad-group, Context Hint, creative, evidence, landing-page,
   budget, and measurement planning artifacts.
5. Validate local structure and supplied data with the offline scripts.
6. Export a plan whose terminal status is `PLAN_READY`.

Every exported plan must contain:

```json
{
  "status": "PLAN_READY",
  "publish_authorized": false,
  "external_writes": false
}
```

No field in a Lite plan can authorize a future write. Local IDs are planning
IDs only; account IDs, live resource IDs, tokens, cookies, API keys, connector
payloads, live schema snapshots, and upload IDs are forbidden.

## Local tools

```bash
python3 scripts/ads_toolkit.py analyze examples/metrics.synthetic.json
python3 scripts/ads_toolkit.py economics examples/economics.synthetic.json
python3 scripts/ads_toolkit.py validate-plan templates/campaign-plan.json
python3 scripts/ads_toolkit.py utm 'https://example.com/product' --campaign trial --content angle-a
python3 scripts/beginner_toolkit.py onboarding templates/beginner-onboarding.json
```

The scripts read and write local files only. A successful local check means the
plan is structurally ready; it does not mean a platform account is eligible,
live capability exists, or any change is approved.

## Contracts

The public interchange artifact is `chatads.plan@1.0`, specified in
`references/data-contract.md`. A future Runmo manifest may identify this Skill
as `skill_id: chatads`, `edition: lite`, with no external reads, writes,
credentials, or network. The future input contract is `chatads.brief@1.0`;
until formalized, business intake remains local input rather than a second
implementation.
