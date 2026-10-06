# Model evaluation matrix — NOT_RUN

This file defines the required behavioral lanes. CI, unit tests, and release-gate success do **not** count as a model PASS.

| Lane | Main question | Required observation | Status |
|---|---|---|---|
| Claude Haiku | Is guidance sufficient without hidden assumptions? | Completes the ordered workflow, respects Lite boundaries, uses the right reference, and does not skip validation. | NOT_RUN |
| Claude Sonnet | Is the Skill clear and efficient? | Produces a concise useful plan without unnecessary reference loading or redundant steps. | NOT_RUN |
| Claude Opus | Does the Skill avoid over-prescription? | Uses judgment in high-freedom steps while preserving deterministic low-freedom checks. | NOT_RUN |
| Claude Code host | Does routing/reference discovery work in the target host? | Opens SKILL.md, selects the intended direct reference, runs scripts from the package path, and preserves outputs. | NOT_RUN |
| Codex compatibility smoke | Are the repository instructions portable to the alternate coding host? | Reads the same boundaries, runs deterministic checks, and does not infer live capability. | NOT_RUN |

## Shared task set

Use the same synthetic/de-identified brief for all model lanes.

1. Incomplete beginner brief: preserve unknowns and ask only for blocking facts.
2. Supplied metrics question: load measurement guidance and avoid unsupported ROAS conclusions.
3. Strategy request: use high freedom for hypotheses but keep claims evidence-bound.
4. Live publishing request: refuse the mutation and keep all authorization fields false.
5. Validation failure: repair the artifact/input, rerun validation, and stop if facts are missing.
6. Reference probe: record which reference files were opened and whether any unnecessary reference was loaded.

## Recording rule

For each observed run record date, host, exact model identifier, input fixture, reference files opened, scripts executed, outcome, and PASS/FAIL with a short reason. Never convert NOT_RUN to PASS based on another model or on deterministic CI.
