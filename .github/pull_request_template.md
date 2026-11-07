## JAR-<number>: <title>

**Jira:** https://muditkumarbhatnagar.atlassian.net/browse/JAR-<number>

### What and why
<!-- What this change does and the problem it solves. -->

### How to verify
<!-- Commands to run or screens to open. -->

### Definition of Done
- [ ] Title and every commit start with the Jira key
- [ ] Tests written first (RED -> GREEN -> REFACTOR) and passing
- [ ] Coverage thresholds met; edge cases and error paths covered
- [ ] Ruff and Pyright clean
- [ ] Verified by hand where applicable
- [ ] No secrets, keys or personal data in the diff
- [ ] ADR added if a significant decision was made
- [ ] Learning-log page added in `docs/learning/`
- [ ] Targets the right branch (`feature/*` -> `dev`, `dev` -> `test`, `test`/`hotfix/*` -> `prod`)
