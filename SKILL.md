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

ChatAds Skill Lite is the free, open-source planning edition. It helps a beginner collect a business brief, translate goals, plan campaigns and ad groups, describe Context Hints, prepare creative and landing-page checks, explore budget scenarios, generate UTM parameters, analyze supplied data, and export a portable `chatads.plan@1.0` artifact.

Lite is offline and planning-focused. It does not connect to Ads Manager, resolve accounts, inspect live schemas, upload creatives, send events, create or update platform objects, or hold credentials. Advanced live operation belongs outside this repository.

## Reference map

Open only the reference needed for the current question. Every runtime reference is linked directly from this file; do not rely on reference-to-reference discovery.

- Beginner intake and sequencing: [references/beginner-workflows.md](references/beginner-workflows.md)
- Public plan contract and safety fields: [references/data-contract.md](references/data-contract.md)
- Supplied metrics and economics interpretation: [references/measurement-and-analysis.md](references/measurement-and-analysis.md)
- Dated source notes and scope: [references/official-sources.md](references/official-sources.md)
- Strategy and creative guidance: [references/strategy-and-creative.md](references/strategy-and-creative.md)

If a reference grows beyond 100 lines, it must have a `## Contents` (or equivalent contents heading) near the top. The release gate enforces this.

## Degrees of freedom

Use the least restrictive method that is safe for the step.

**High freedom — judgment is expected**
- Explain the brief in plain language.
- Form strategy or creative hypotheses from supplied facts.
- Suggest questions, tests, and trade-offs without inventing platform capability.

**Medium freedom — preserve the shape, vary the content**
- Fill the local campaign/ad-group planning structure.
- Produce creative briefs, landing-page checks, and measurement summaries.
- Keep facts, assumptions, unknowns, and recommendations visibly separate.

**Low freedom — execute deterministically**
- Economics, UTM generation, contract validation, authorization flags, and release checks.
- Run the provided script as documented; do not replace deterministic calculations with model arithmetic.
- Never weaken validation to make an artifact pass.

## Ordered execution checklist

Use this checklist when the request spans planning plus validation. Keep it as concise execution state; do not expose hidden reasoning.

- [ ] Collect only missing business facts and preserve unknowns.
- [ ] Select the smallest relevant references from the reference map.
- [ ] Draft the local plan or supplied-data interpretation.
- [ ] Run the appropriate deterministic script or validator.
- [ ] If validation fails, repair the failing input/structure and validate again.
- [ ] Deliver only after deterministic checks pass or clearly report the blocker.

If a check fails, return to the failing step. Do not mark the task complete and continue past a failed validator.

## Self-correction loop

For deterministic artifacts: **draft → validate → repair → revalidate**. Repeat until the validator passes or missing user facts make further repair impossible. Repair the artifact or input, never the validator.

For high-freedom prose: review the draft against supplied facts, the relevant reference, Lite boundaries, and unsupported-claim risk. Revise factual or scope violations before finalizing.

`PLAN_READY` means the local artifact is structurally ready for human review. It never means approved, published, eligible, or safe to spend.

## Dependencies

Required: Python 3.10+ and its standard library only. No `pip install`, npm, Docker, API key, browser session, connector, network access, or sibling repository is required.

If Python 3.10+ is unavailable, stop and report the missing prerequisite instead of silently installing software. A host model may be used for separate interpretation; model/provider access is not a package dependency.

## Workflow

1. Ask for the offer, customer, goal, market, landing page, total spend limit, and measurable success action.
2. Keep missing facts as questions or unknowns; do not invent product claims, prices, budgets, tracking access, or platform support.
3. Translate the goal into local planning intent such as `reach`, `clicks`, or `conversions`. These are planning labels, not live platform enums.
4. Build campaign, ad-group, Context Hint, creative, evidence, landing-page, budget, and measurement planning artifacts.
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

No field in a Lite plan can authorize a future write. Local IDs are planning IDs only; account IDs, live resource IDs, tokens, cookies, API keys, connector payloads, live schema snapshots, and upload IDs are forbidden.

## Local tools

```bash
python3 scripts/ads_toolkit.py analyze examples/metrics.synthetic.json
python3 scripts/ads_toolkit.py economics examples/economics.synthetic.json
python3 scripts/ads_toolkit.py validate-contract templates/campaign-plan.json
# Detailed campaign/preflight checks use a detailed planning fixture.
python3 scripts/ads_toolkit.py validate-plan <detailed-campaign-plan.json>
python3 scripts/ads_toolkit.py utm 'https://example.com/product' --campaign trial --content angle-a
python3 scripts/beginner_toolkit.py onboarding templates/beginner-onboarding.json
```

The scripts read and write local files only. A successful local check means the plan is structurally ready; it does not mean a platform account is eligible, live capability exists, or any change is approved.

`validate-contract` checks the public `chatads.plan@1.0` envelope and Lite safety
invariants. `validate-plan` remains the detailed campaign/preflight completeness
check and expects its separate detailed planning schema.

## Contracts

The public interchange artifact is `chatads.plan@1.0`, specified in [references/data-contract.md](references/data-contract.md). A future Runmo manifest may identify this Skill as `skill_id: chatads`, `edition: lite`, with no external reads, writes, credentials, or network. The future input contract is `chatads.brief@1.0`; until formalized, business intake remains local input rather than a second implementation.

## Evaluation status

Structural and deterministic CI checks are automated. Cross-model behavior is not implied by CI. Use [evals/MODEL_EVAL_MATRIX.md](evals/MODEL_EVAL_MATRIX.md) and record observed runs before marking a model lane PASS.
