# Maintainers

## Current maintainer

- [@ckolpeter](https://github.com/ckolpeter)

## Maintainer responsibilities

Maintainers are responsible for:

- issue triage
- pull request review
- ChatAds Plan Contract compatibility
- Lite boundary enforcement
- dependency and security review
- release preparation
- documentation quality

## Release workflow

Before a release:

1. Review all included changes.
2. Run the complete unit test suite.
3. Run `py_compile` for the Lite scripts.
4. Validate all JSON files.
5. Run `python3 scripts/lite_release_gate.py`.
6. Regenerate and verify `MANIFEST.sha256`.
7. Confirm the Git diff and working tree are clean.
8. Create a semantic-version tag.
9. Publish a GitHub Release.

No merge or release should bypass Lite boundary checks.

## Maintainer principles

- Prefer conservative, reviewable changes.
- Treat `chatads.plan` as a public compatibility contract.
- Keep Lite offline and non-authorizing.
- Do not merge secrets, live customer/account data, or Pro-only execution logic.
