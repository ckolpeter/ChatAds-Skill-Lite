# ChatAds Skill Lite 1.1.0 | English

[← Back to the main README](../../README.md)

Offline ad planning for business briefs, campaign/ad-group structure, Context Hints, creative briefs, budget scenarios, UTM generation, supplied-data analysis, and local validation.

## What it does

- Produces a local, human-reviewable advertising-planning draft from supplied information.
- Keeps unknown facts unknown instead of inventing account state, performance, pricing, permissions, or platform capabilities.
- Can be used with a host model such as Codex or Claude Code for language refinement, followed by local validation.

## What it does not do

Lite does not sign in to ad accounts, store credentials, call advertising-platform APIs, read live account data, or create, publish, and mutate live ads. PLAN_READY means the local planning artifact is ready for human review only.

## Quick start

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ads_toolkit.py analyze examples/metrics.synthetic.json
python3 scripts/ads_toolkit.py economics examples/economics.synthetic.json
python3 scripts/lite_release_gate.py
```

Requirement: Python 3.10+. The package itself needs no API key, npm, or Docker.

## Languages and safety

Documentation is available in Traditional Chinese, Simplified Chinese, English, Japanese, and Korean. Agent output should follow the user's language. Do not provide unredacted customer personal data or advertising credentials to a model.

This project is not an official OpenAI product and does not connect to or modify live advertising accounts.\n\nAI Ads Academy: https://www.ai-ads.academy

License: Apache-2.0.
