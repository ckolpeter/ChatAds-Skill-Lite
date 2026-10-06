# ChatAds Skill Lite

[繁體中文](docs/i18n/README.zh-TW.md) · [简体中文](docs/i18n/README.zh-CN.md) · [English](docs/i18n/README.en.md) · [日本語](docs/i18n/README.ja.md) · [한국어](docs/i18n/README.ko.md)

**Website:** https://www.ai-ads.academy

ChatAds Skill Lite is the free, open-source, offline planning edition of ChatAds Skill. It exports `chatads.plan@1.0` and never performs live advertising mutations.

The public package includes onboarding, campaign and ad-group planning, Context Hint and creative briefs, budget scenarios, economics, landing-page readiness, UTM generation, supplied-data analysis, metrics translation, and local plan validation.

Run from this directory:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ads_toolkit.py analyze examples/metrics.synthetic.json
python3 scripts/ads_toolkit.py economics examples/economics.synthetic.json
python3 scripts/ads_toolkit.py validate-contract templates/campaign-plan.json
python3 scripts/beginner_toolkit.py onboarding templates/beginner-onboarding.json
python3 scripts/lite_release_gate.py
```

Python 3.10+ and the standard library are sufficient. Lite has no network, credential, connector, Runmo, or Pro package dependency.

Best-practices hardening: [audit](docs/BEST_PRACTICES_AUDIT.md) · [model eval matrix](evals/MODEL_EVAL_MATRIX.md). Cross-model lanes remain NOT_RUN until observed.

License: Apache-2.0
