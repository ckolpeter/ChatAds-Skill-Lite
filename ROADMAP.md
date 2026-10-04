# ChatAds Skill Lite Roadmap

This roadmap describes the current direction for ChatAds Skill Lite. It is directional, not a commitment or delivery schedule.

## Current

### v1.0.0 — Released

- Beginner-first offline advertising planning
- Campaign and ad-group planning
- Context Hint planning
- Budget scenarios and economics
- Landing-page readiness
- UTM generation
- Supplied-data analysis and metrics translation
- `chatads.plan@1.0` planning contract
- Lite release boundary checks
- Apache-2.0 licensing

## Next

### v1.1

- Define a formal JSON Schema for ChatAds Plan Contract v1
- Formalize the `chatads.brief@1.0` input contract
- Add a dedicated plan export command
- Expand negative and adversarial test coverage
- Add examples for multiple advertising scenarios

### v1.2

- Add cross-version contract compatibility tests
- Improve offline reporting
- Add contributor-supplied synthetic fixtures
- Improve documentation and localization

## Future

- Maintain serialized compatibility with ChatAds Skill Pro through `chatads.plan`
- Define a Runmo compatibility specification without coupling Lite to Runmo
- Keep Lite offline and planning-only; live advertising mutations remain outside Lite scope

## Non-goals

ChatAds Skill Lite will not become a live ad-account operator. It does not store credentials, resolve live accounts, publish campaigns, upload creatives, or spend advertising budget.
