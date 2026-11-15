# JARVIS

A personal AI companion that reads what you give it, remembers what you allow, and acts only where you permit.

Upload textbook pages, novels, research papers or web links; ask questions with page citations, generate quizzes,
mind maps and audio summaries, talk to characters from your books, and (later) control your own laptop from your phone.

> Status: Phase 0 (foundations). Built as a learning project in Python AI backend engineering.

## Branches

| Branch | Purpose |
|--------|---------|
| `dev`  | Integration branch (default). Feature branches merge here. |
| `test` | Release candidates, promoted from `dev`. |
| `prod` | Released, tagged versions, promoted from `test`. |

Work is tracked in Jira (project key `JAR`). See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow.

## Getting started

Requirements: [uv](https://docs.astral.sh/uv/), Git, Docker (from JAR-4), Node 22 (from JAR-8).

```bash
git clone https://github.com/mudit1024/jarvis.git && cd jarvis
uv sync                       # installs Python tools at the exact locked versions
uv run pre-commit install     # installs the git hooks
uv run pytest                 # runs the tests
```

## Documentation

* [CONTRIBUTING.md](CONTRIBUTING.md): workflow, branches, TDD, Definition of Done
* [docs/adr/](docs/adr/): architecture decision records
* [docs/learning/](docs/learning/): learning log, one page per Jira issue
