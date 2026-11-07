# Contributing to JARVIS

These rules follow the SplitMate workflow, adapted for Python and a three-branch (dev, test, prod) model.
The full reasoning is in the Technical Design document, section 16.

## 1. Jira-first development

Every unit of work has a Jira issue (project key `JAR`) before implementation begins.

```text
Jira issue -> Branch -> TDD RED -> Develop -> TDD GREEN -> Refactor -> Test & coverage
-> Commit -> Push -> Pull request -> CI / review -> Merge -> Branch cleanup -> Jira Done
```

* Create the Jira issue before creating a branch, and assign it to yourself.
* Move it to `In Progress` when work begins and to `Done` only when the Definition of Done is met.
* One issue per user-facing feature or meaningful technical unit, with a checklist for its steps.
* The Jira key appears in the branch name, every commit, and the pull request title.

## 2. Branches

Three long-lived branches. There is no `main`.

| Branch | Holds                                   | Accepts pull requests from          |
|--------|-----------------------------------------|-------------------------------------|
| `dev`  | Every finished feature (default branch) | `feature/*`, `bugfix/*`             |
| `test` | Release candidate being verified        | `dev` only                          |
| `prod` | Released, tagged versions               | `test` only, or `hotfix/*`          |

```text
feature/JAR-12-login ──PR──> dev ──promotion PR──> test ──release PR──> prod  (tag vX.Y.Z)
```

Short-lived branches:

```text
feature/JAR-<n>-<short-description>   from dev   -> PR into dev
bugfix/JAR-<n>-<short-description>    from dev   -> PR into dev
hotfix/JAR-<n>-<short-description>    from prod  -> PR into prod, then back-merge prod -> test -> dev
```

Rules:

* Never commit directly on `dev`, `test` or `prod` (a pre-commit hook refuses it; branch protection enforces it on GitHub).
* Branch from the latest `dev`: `git switch dev && git pull && git switch -c feature/JAR-<n>-...`
* Run `git status` before switching branches; never switch with uncommitted work.
* Merge with merge commits (not squash), so the three branches keep a shared history.

### Promotion and releases

1. **dev -> test**: when a group of features is ready (at least at every phase milestone), open a pull request
   titled `Promote to test: <phase or date>`. CI runs the full suites; verify by hand.
2. **test -> prod**: open a pull request titled `Release vX.Y.Z`. After merging, tag the release on `prod`:
   `git tag -a vX.Y.Z -m "Release vX.Y.Z" && git push origin vX.Y.Z`, and create the matching Jira release.
3. Versions are semantic. Until the first public release: one minor version per phase (v0.1.0 = Phase 0),
   patch versions for hotfixes.

## 3. Commits

Format (checked by the `commit-msg` hook in `tools/commit_msg.py`):

```text
JAR-<number>: <short description in the imperative>
```

Example: `JAR-2: add pre-commit hooks`. Merge and revert messages written by git are allowed.

## 4. Test-driven development

1. **RED**: write a test that describes the expected behaviour; run it and watch it fail.
2. **GREEN**: write the minimum production code that makes it pass.
3. **REFACTOR**: improve the code while the tests stay green.
4. Run the suite, check coverage, add edge-case and error-path tests.

* Tests describe observable behaviour, are deterministic and independent.
* Every bug fix starts with a regression test.
* Unit tests never call a real AI model: they use a fake gateway. Model quality is measured by the evaluation suite.
* No test is written only to raise coverage.

### Coverage targets

| Area                                  | Target                                      |
|---------------------------------------|---------------------------------------------|
| Services / business logic             | 90-95%+                                     |
| API layer                             | 85-95%+                                     |
| Security, auth, device-agent policy   | Very high (~100% branch on policy code)     |
| Overall backend                       | 90%+ (enforced in CI)                       |
| Repositories                          | Meaningful integration tests on PostgreSQL  |

## 5. Local setup

```bash
uv sync                      # create .venv and install the exact locked tool versions
uv run pre-commit install    # install the git hooks (once per clone)
uv run pytest                # tests
uv run ruff check . && uv run ruff format --check . && uv run pyright
```

## 6. Definition of Done

* Implementation complete; Ruff and Pyright clean
* Tests written first and passing; coverage thresholds met
* Verified by hand (API docs page `/docs` or the app) where applicable
* CI passes
* Pull request self-reviewed with the template checklist and merged into `dev`
* Feature branch deleted locally and remotely
* Learning-log page written in `docs/learning/`
* Jira issue moved to `Done`

## 7. Decisions

Significant technical decisions are recorded as Architecture Decision Records in `docs/adr/`
(copy `0000-template.md`) and linked from the Jira issue.
