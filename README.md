# ChatAds Skill Lite

ChatAds Skill Lite is the free, open-source, offline planning edition of ChatAds Skill. It exports `chatads.plan@1.0` and never performs live advertising mutations.

The public package includes onboarding, campaign and ad-group planning, Context Hint and creative briefs, budget scenarios, economics, landing-page readiness, UTM generation, supplied-data analysis, metrics translation, and local plan validation.

Run from this directory:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ads_toolkit.py analyze examples/metrics.synthetic.json
python3 scripts/ads_toolkit.py economics examples/economics.synthetic.json
python3 scripts/beginner_toolkit.py onboarding templates/beginner-onboarding.json
python3 scripts/lite_release_gate.py
```

Python 3.10+ and the standard library are sufficient. Lite has no network, credential, connector, Runmo, or Pro package dependency.
