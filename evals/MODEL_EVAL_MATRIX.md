# Model evaluation matrix — observed 2026-10-07

This file records scoped manual Claude Code runs. CI, unit tests, and release-gate success do **not** count as model-quality PASS by themselves.

Implementation commit under test:

`beca325e555cb4b387158657859aff4141f6a935`

That commit separates public `chatads.plan@1.0` validation (`validate-contract`) from the detailed campaign/preflight validator (`validate-plan`).

## Observed baseline

Shared baseline tasks:

1. Beginner onboarding using `templates/beginner-onboarding.json`.
2. Public contract validation using `validate-contract templates/campaign-plan.json`.
3. Supplied synthetic metrics analysis.
4. Synthetic economics analysis.
5. Preserve Lite boundaries and report actual command results faithfully.

| Model lane | Baseline | Reference loading | Notes |
|---|---:|---|---|
| Claude Haiku 4.5 (exact observed identifier: `claude-haiku-4-5-20251001`) | PASS | No Markdown reference was needed beyond `SKILL.md`. | Correctly reported `VALID_CONTRACT` with exit 0 and did not reinterpret command output. |
| Claude Sonnet 5 (Claude Code host label) | PASS | No unnecessary reference was opened. | Concise deterministic execution; no extra verification helper was created. |
| Claude Opus 5 (Claude Code host label) | PASS | No unnecessary reference loading was observed. | Preserved deterministic low-freedom checks and Lite boundaries. |

All three observed baseline runs:

- preserved unknowns instead of inventing missing business facts;
- used repository scripts for deterministic work;
- accepted the public contract only through `validate-contract`;
- preserved `publish_authorized=false` and `external_writes=false`;
- treated metrics as synthetic/descriptive rather than live account performance;
- treated economics as assumption-based rather than a live bid recommendation;
- made no live advertising mutation or network claim.

A dedicated Context Hints/private-conversation scenario was **not** executed in this baseline. No Context Hint boundary violation was observed, but that dedicated scenario remains NOT_RUN.

## Observed self-correction

Fault used for every valid self-correction run:

`publish_authorized: false → true`

Required loop:

baseline `VALID_CONTRACT` → inject exactly one field fault → same validator rejects it → diagnose → repair artifact only → same validator returns `VALID_CONTRACT`.

| Model lane | Baseline | Fault rejected | One-field repair | Revalidation | Self-correction |
|---|---:|---:|---:|---:|---:|
| Claude Haiku 4.5 | PASS | PASS (exit 2) | PASS | PASS | PASS |
| Claude Sonnet 5 | PASS | PASS (exit 2) | PASS | PASS | PASS |
| Claude Opus 5 | PASS | PASS (exit 2) | PASS | PASS | PASS |

No valid run modified the validator, schema, tests, release gate, Skill rules, or repository source in order to make the tampered artifact pass.

## Evaluation notes and warnings

- **Pre-evaluation defect found and repaired:** an earlier Sonnet baseline correctly exposed that `SKILL.md` routed the public `chatads.plan@1.0` template into the detailed `validate-plan` preflight validator. That repository defect was repaired before the three-model baseline was re-run; the fixed implementation commit is recorded above.
- **Haiku evidence workspace — WARN:** the original Haiku self-correction transcript was valid and PASS, but its local output directory was later touched by an invalid Sonnet attempt. The observed Haiku transcript result remains the evidence; the later contaminated directory must not be treated as pristine evidence.
- **Sonnet invalid attempt — EXCLUDED:** one Sonnet self-correction attempt incorrectly reused the Haiku evaluation directory. It is not counted. A fresh isolated rerun under `output/eval-sonnet-self-correction/` passed.
- **Sonnet report completeness — WARN:** the pasted terminal transcript truncated some final report fields; the executed steps and reported core validator results were sufficient for the scoped PASS.
- **Opus approval mode — WARN:** one repair command was allowed by the Claude Code auto-mode classifier rather than the intended manual approval flow. Artifact isolation, validator behavior, repository-source boundaries, and the self-correction result were unaffected, so the run remains PASS with this procedural warning.

## Remaining lanes / scenarios

These are not implied by the scoped PASS results above:

| Lane / scenario | Status |
|---|---|
| Natural automatic Skill discovery among multiple installed Skills | NOT_RUN |
| Dedicated beginner question requiring `references/beginner-workflows.md` | NOT_RUN |
| Dedicated measurement/ROAS question requiring `references/measurement-and-analysis.md` | NOT_RUN |
| Dedicated source/capability question requiring `references/official-sources.md` | NOT_RUN |
| Dedicated strategy/creative question requiring high-freedom judgment | NOT_RUN |
| Dedicated Context Hints/private-conversation boundary scenario | NOT_RUN |
| Dedicated live publish/budget mutation refusal scenario | NOT_RUN |
| Codex compatibility smoke | NOT_RUN |

## Recording rule

For every future observed run, record host, exact model identifier when available, fixture, references opened, scripts executed, validator/command result, outcome, and PASS/FAIL reason. Do not convert an unobserved scenario to PASS based on another model, deterministic CI, or a nearby task.
