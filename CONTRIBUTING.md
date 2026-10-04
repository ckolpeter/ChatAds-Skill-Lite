# Contributing to ChatAds Skill Lite

Thanks for contributing to ChatAds Skill Lite.

The project is Apache-2.0 licensed and intentionally keeps a narrow public boundary: beginner-first, offline advertising planning with no live ad-account mutations.

## Development requirements

- Python 3.10+
- Standard library only for Lite runtime code
- No network, credential, connector, Runmo, or Pro runtime dependency

## Setup and validation

From the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/ads_toolkit.py scripts/beginner_toolkit.py scripts/lite_release_gate.py
python3 scripts/lite_release_gate.py
```

Validate JSON files:

```bash
python3 - <<'PY'
import json
from pathlib import Path

for path in sorted(Path(".").rglob("*.json")):
    if ".git" in path.parts:
        continue
    json.loads(path.read_text(encoding="utf-8"))
    print(f"{path}: OK")
PY
```

Verify the release manifest:

```bash
sha256sum -c MANIFEST.sha256
```

On macOS:

```bash
shasum -a 256 -c MANIFEST.sha256
```

## Regenerating MANIFEST.sha256

When a release-tracked file is added or changed, regenerate the manifest from the repository root:

```bash
python3 - <<'PY' > MANIFEST.sha256
from pathlib import Path
import hashlib

root = Path(".")
paths = [
    p for p in root.rglob("*")
    if p.is_file()
    and ".git" not in p.parts
    and p.as_posix() != "MANIFEST.sha256"
]
for path in sorted(paths, key=lambda p: p.as_posix()):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{digest}  {path.as_posix()}")
PY
```

Then verify the result before committing.

## Pull request expectations

- Prefer one concern per pull request when practical.
- Add or update tests for behavior changes.
- Update documentation when changing a contract or user-facing workflow.
- Explain compatibility impact for any `chatads.plan` change.
- Keep synthetic fixtures free of customer data, credentials, live account IDs, and private campaign data.
- Ensure the full test suite and Lite release gate pass.

## Lite boundary

Contributions must not add:

- live ad-account access
- Ads Manager connector calls
- external advertising writes
- credential or secret persistence
- Pro runtime behavior

The terminal planning state is `PLAN_READY`.

The following invariants must remain true:

```json
{
  "publish_authorized": false,
  "external_writes": false
}
```

## Contract changes

Breaking changes to `chatads.plan` require an issue before implementation.

A proposal should describe:

- the problem
- the contract fields affected
- backward-compatibility impact
- migration or versioning strategy
- positive and negative test cases

Unsupported major contract versions should fail closed rather than being silently coerced.

## Security and privacy

Do not include API keys, cookies, access tokens, real ad-account IDs, private campaign exports, customer identifiers, or other secrets in issues, pull requests, examples, or tests.
