# Best-practices retrofit audit — 2026-10-06

Scope: ChatAds Skill Lite only. This is an implementation audit, not Anthropic certification and not a live advertising validation.

| Check | Result | Evidence |
|---|---|---|
| SKILL.md stays below 500 lines | PASS | Enforced by `scripts/lite_release_gate.py`. |
| Runtime references are one hop from SKILL.md | PASS | Every `references/*.md` is listed in the SKILL reference map; nested reference directories are rejected. |
| Reference files over 100 lines have a top content list | PASS (guarded) | No current reference exceeds 100 lines; the release gate will fail future long references without a contents heading. |
| Degrees of freedom are explicit | PASS | High/medium/low guidance is defined in SKILL.md. |
| Ordered multi-step work has a checklist | PASS | SKILL.md contains an ordered execution checklist with a return-on-failure rule. |
| Deterministic work uses scripts | PASS | Economics, UTM, contract validation and release checks remain script-owned. |
| Self-correction loop exists | PASS | Draft → validate → repair → revalidate is explicit; validators may not be weakened. |
| Dependencies are explicit and portable | PASS | Python 3.10+ standard library only; no third-party runtime dependency. |
| Cross-model evaluation | NOT_RUN | Required lanes are defined in `evals/MODEL_EVAL_MATRIX.md`; observed model runs are still required. |

## Release policy

Structural hardening is release-gated. Model quality is reported separately and must remain NOT_RUN until observed in the target host/model. A deterministic PASS does not imply model-quality PASS, platform eligibility, publication approval, or advertising performance.
