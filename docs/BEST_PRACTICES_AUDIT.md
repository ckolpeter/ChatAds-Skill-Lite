# Best-practices retrofit audit — 2026-10-07

Scope: ChatAds Skill Lite only. This is an implementation and scoped behavior audit, not Anthropic certification, OpenAI platform certification, live advertising validation, publication approval, or performance evidence.

Implementation commit used for the observed Claude Code model evaluation:

`beca325e555cb4b387158657859aff4141f6a935`

| Check | Result | Evidence |
|---|---|---|
| SKILL.md stays below 500 lines | PASS | Enforced by `scripts/lite_release_gate.py`. |
| Runtime references are one hop from SKILL.md | PASS | Every `references/*.md` is listed in the SKILL reference map; nested reference directories are rejected. |
| Reference files over 100 lines have a top content list | PASS (guarded) | No current reference exceeds 100 lines; the release gate fails future long references without a contents heading. |
| Degrees of freedom are explicit | PASS | High/medium/low guidance is defined in `SKILL.md`. |
| Ordered multi-step work has a checklist | PASS | `SKILL.md` contains an ordered execution checklist with a return-on-failure rule. |
| Deterministic work uses scripts | PASS | Economics, UTM, public contract validation, detailed preflight validation, and release checks remain script-owned. |
| Public contract / preflight separation | PASS | `validate-contract` validates `chatads.plan@1.0`; `validate-plan` retains detailed campaign/preflight semantics. |
| Self-correction loop exists | PASS | Draft → validate → repair → revalidate is explicit; validators may not be weakened. |
| Self-correction loop behavior | PASS (scoped) | Haiku 4.5, Sonnet 5, and Opus 5 each rejected a `publish_authorized=true` tamper, repaired only the artifact, and revalidated successfully. |
| Dependencies are explicit and portable | PASS | Python 3.10+ standard library only; no third-party runtime dependency. |
| Cross-model baseline behavior | PASS (scoped) | Haiku 4.5, Sonnet 5, and Opus 5 completed the same onboarding/contract/metrics/economics baseline on the recorded implementation commit. |
| Full host/model scenario matrix | PARTIAL | Automatic multi-Skill discovery, reference-specific probes, strategy, Context Hints, dedicated live-mutation refusal, and Codex compatibility remain NOT_RUN. |

## Evaluation-quality notes

The model-evaluation process itself caught a real repository interface defect: the public contract template was initially routed to the detailed preflight validator. The defect was repaired before the three-model baseline was repeated.

One Sonnet self-correction attempt was excluded because it reused the Haiku workspace; a fresh isolated Sonnet rerun passed. The original Haiku transcript remains valid, although its local output directory was later contaminated by that excluded Sonnet run. The Opus self-correction run passed with a procedural warning because one command used the host's auto-mode classifier rather than manual approval.

## Release interpretation

Structural CI plus the scoped three-model baseline and self-correction PASS provide stronger confidence in deterministic delegation, public contract validation, command-result fidelity, Lite safety boundaries, and artifact repair/revalidation behavior for the tested fixtures.

They do **not** prove automatic Skill discovery, every reference-routing branch, live platform capability, account eligibility, policy compliance, publication approval, budget mutation safety in a live system, or advertising performance.

Detailed observed results and remaining scenarios are recorded in `evals/MODEL_EVAL_MATRIX.md`.
