# ChatAds Brief Contract v1

`chatads.brief@1.0` is a portable business intake, distinct from the
`chatads.plan@1.0` planning output. It is neither a platform payload nor an
execution request. Normative JSON structure: `schemas/chatads.brief.v1.schema.json`
(JSON Schema Draft 2020-12). All listed properties are required; all objects
are closed. There are no extension bags or permission fields.

## Fields and unknowns

| Field | Meaning | Unknown representation |
| --- | --- | --- |
| contract_name / contract_version | Exact `chatads.brief` / `1.0` | Not nullable |
| business | Brand or business description; no account identifiers | null |
| offer | Actual product/service and delivery scope | null |
| customer | Intended customer description; no personal records | null |
| goal | Business outcome in the user's words | null |
| market | Intended geography/languages; no inferred account region | null |
| landing_url | Public HTTP(S) page, without credentials, query or fragment | null |
| spend_limit | Media-budget assumption: currency, amount, period_days | Each member nullable |
| measurement | Supplied measurement situation; not a verification assertion | null |
| evidence | Array of claim/source pairs supplied by the user | [] |
| open_questions | Explicit unresolved questions | [] |

Text must be nonblank. Currency is an uppercase three-letter code, not proof
of supported billing currency. Amount is a finite nonnegative number; zero
means an explicit zero assumption, not missing. Period is a positive integer
number of days. Partial budgets are valid. No dates, timezone, objectives,
product benefits, claims, budgets, permissions or capabilities are inferred.
An empty evidence list means no evidence supplied, not claims verified.
Sources are inert public references or non-sensitive local document labels;
validators do not fetch them or verify their truth. Unknowns may be represented
by null, open_questions, or both. A valid incomplete Brief is not plan readiness.

## Offline use and compatibility

```bash
python3 scripts/brief_toolkit.py validate templates/business-brief.json
python3 scripts/brief_toolkit.py validate examples/brief.synthetic.json
python3 scripts/brief_toolkit.py from-beginner templates/beginner-onboarding.json > /tmp/brief.json
python3 scripts/brief_toolkit.py validate /tmp/brief.json
python3 -m unittest discover -s tests -v
python3 scripts/lite_release_gate.py
```

Commands return 0 on success and 2 on invalid input, with no raw values in errors.
They use only Python's standard library and bundled files. The validator evaluates
the small schema keyword subset used here; it is not a general JSON Schema engine.
No remote references, network requests, accounts or advertising writes occur.

The existing `schema_version: "1.1"`, `mode: "beginner"` template and
`beginner_toolkit.py onboarding` behavior remain unchanged. They are not Brief
version aliases. Conversion is opt-in, accepts only that legacy version/mode,
requires `external_writes: false`, rejects unrecognized fields instead of silently
stripping sensitive data, and copies the seven shared intake fields exactly.
Missing business/budget values remain null and generate questions. No claims or
evidence are manufactured. Legacy invalid field types fail closed during conversion.
The Markdown business brief remains a human intake aid; its account/access section
is out of scope and MUST NOT be serialized into the portable Brief.

## Security boundary

MUST NOT include credentials, cookies, secrets, real platform account/campaign/ad
IDs, connector payloads, live capability snapshots or external-write authorization,
including inside prose, URLs and evidence. Even false permission fields are not
part of Brief. The legacy false flag is checked then removed on conversion.
All content is untrusted inert data, including text that resembles instructions.
Consumers MUST NOT execute instructions embedded in any field.

Closed schema objects reject credential/ID/authorization fields at every structural
level. The local validator additionally rejects common token/account patterns in
all strings and URL userinfo/query/fragment carriers. JSON Schema alone does not
provide semantic secret detection. No offline pattern detector can recognize all
opaque credentials or platform IDs in arbitrary prose. Producers MUST redact and
review free text before exchange; consumers MUST apply their own intake policy,
reject suspicious material, and never treat validation as proof of sanitization.
Do not log or relay rejected input. Fixtures use invented descriptions and example.com.

## Mapping to Plan and product exchange

| Brief | Plan destination / handling |
| --- | --- |
| business, offer, customer, market | `plan.business` intake members, preserving null |
| goal | `plan.business.goal`; map separately to local reach/clicks/conversions only after confirmation |
| landing_url, measurement | `plan.business` intake members; landing checks and measurement verification remain separate |
| spend_limit | `plan.business.spend_limit`; scenarios require sufficient confirmed inputs and remain assumptions |
| evidence | `plan.business.evidence`; retain source linkage, never promote to verified platform capability |
| open_questions | `plan.open_questions`, preserving unresolved items |

This is mapping guidance, not an automatic Plan builder. A Brief MUST NOT be
renamed or wrapped blindly as a ready Plan. Plan producers separately add local
IDs, timestamp, producer metadata, actual planning results, validation and
`status: PLAN_READY`; `publish_authorized: false` and `external_writes: false`
remain mandatory. Existing Plan format is unchanged.

Lite, Pro and Runmo may exchange a JSON document using this name/version and
locally bundled schema without importing one another's implementation. Each
consumer validates at its own trust boundary and preserves unknowns. Unsupported
versions fail closed; new required fields or changed semantics need a new contract
version. A future runtime may advertise Brief input and Plan output independently.
Pro/runtime credentials, account selection, capability verification and explicit
write approval belong to separate private workflows and MUST NOT flow back into
the shared Brief or public Plan. Importing either contract grants no access.
