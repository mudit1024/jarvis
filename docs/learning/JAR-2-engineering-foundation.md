# JAR-2: Engineering foundation

**Goal:** before writing any application code, set up the tools that keep every later line of code consistent,
checked and traceable. Nothing here is "AI" yet; it's the ground the AI backend will stand on.

---

## 1. uv: the Python project and package manager

### What problem it solves
Python projects need three things that Java gives you through Maven:

| Need | Java / Maven | Python (old way) | Python with uv |
|------|--------------|------------------|----------------|
| A file listing the project and its dependencies | `pom.xml` | `requirements.txt` / `setup.py` | `pyproject.toml` |
| Download libraries | `mvn install` (to `~/.m2`) | `pip install` | `uv sync` / `uv add` |
| Isolate this project's libraries from other projects | Classpath per project, automatic | Create a *virtual environment* by hand (`python -m venv`) | `uv` creates `.venv/` for you |
| Exact, repeatable versions | Pinned versions in the POM | `pip freeze` (manual) | `uv.lock` (automatic) |
| Run a tool with the project's libraries | `mvn exec:java` / `./mvnw` | Activate the venv first | `uv run <command>` |

**Virtual environment (`.venv/`)**: a private folder with its own Python and libraries for this project only.
In Java every project has its own classpath automatically; in Python, without a venv, all projects share one
global set of libraries and their versions collide. uv makes the venv for you and never needs "activating".

**Lockfile (`uv.lock`)**: `pyproject.toml` says "pytest version 9.2 or newer"; `uv.lock` records the *exact*
version of pytest **and of every library it depends on** that was installed. Anyone (or CI) running `uv sync`
gets the identical set. It's committed to Git. Never edit it by hand.

**Why uv and not pip?** It's 10-100x faster (written in Rust), manages Python versions, venvs, dependencies and
lockfiles in one tool, and has become the industry default for new projects.

### Commands we used
```bash
winget install astral-sh.uv        # install uv (Windows package manager)
uv --version                       # check it works
uv add --dev ruff pyright pre-commit pytest   # add developer tools; updates pyproject.toml + uv.lock
uv sync                            # create .venv and install exactly what uv.lock says
uv run pytest                      # run a command inside the project's environment
```

### pyproject.toml, line by line (the important parts)
* `[project]`: name, version, `requires-python = ">=3.13,<3.14"` (only Python 3.13 is allowed).
* `[dependency-groups] dev = [...]`: tools used while developing (like Maven's `<scope>test</scope>`),
  never shipped with the application.
* `[tool.uv] package = false`: this root folder is a container for the monorepo, not a library to install.
  In JAR-4 the backend becomes a *workspace member* (like a Maven module under a parent POM).
* `[tool.ruff]`, `[tool.pyright]`, `[tool.pytest.ini_options]`: settings for each tool live in the same file.
* `.python-version`: tells uv which Python to use (3.13).

---

## 2. Ruff: linter and formatter

* **Linter**: reads code without running it and reports likely bugs and bad practice
  (unused imports, shadowed names, `assert` in production code, insecure calls). Java equivalent: Checkstyle,
  PMD, SpotBugs, SonarLint (the warnings your IDE shows on SplitMate).
* **Formatter**: rewrites code to one consistent layout (spaces, quotes, line breaks). Java equivalent: Spotless
  or IntelliJ's "Reformat code". No more style discussions: the formatter decides.

The rule sets we enabled (`select = [...]` in pyproject.toml): `E/W` style, `F` real errors (undefined names,
unused imports), `I` import order, `B` likely bugs, `UP` modern syntax, `N` naming, `SIM` simplifications,
`S` security, `PT` pytest style, `RUF` Ruff's own. In tests we allow `S101` (`assert`), because that's how
pytest tests are written.

```bash
uv run ruff check .           # lint
uv run ruff check . --fix     # lint and apply safe fixes
uv run ruff format .          # format
uv run ruff format --check .  # only report files that would change (what CI does)
```

---

## 3. Pyright: static type checking

Java checks types when you compile: `String name = 5;` doesn't compile. Python normally doesn't check types
at all; a wrong type is discovered only when that line runs, possibly in production.

**Type hints** add the information back:
```python
def is_valid_message(message: str) -> bool:   # takes a str, returns a bool
```
Python itself ignores these hints at runtime. **Pyright** reads them and reports mistakes *before* the code runs,
like the Java compiler does. We use `typeCheckingMode = "strict"`, which also requires hints everywhere and
rejects values of unknown type. Strict mode is demanding at first and pays off as the codebase grows. (Pyright
also powers Pylance, the Python support in VS Code, so you see the same errors in the editor.)

```bash
uv run pyright    # 0 errors, 0 warnings expected
```

---

## 4. pytest and our first TDD cycle

### pytest compared with JUnit 5
| JUnit 5 | pytest |
|---------|--------|
| `@Test void acceptsKey()` in a class | `def test_accepts_key():` (any function starting with `test_`) |
| `assertTrue(x)`, `assertEquals(a, b)` | plain `assert x`, `assert a == b` (pytest shows both values on failure) |
| `@ParameterizedTest` + `@ValueSource` | `@pytest.mark.parametrize("message", [...])` |
| `@TempDir Path dir` | the `tmp_path` fixture (a fresh temporary folder per test) |
| Capturing `System.err` | the `capsys` fixture |
| `@BeforeEach`, injected objects | **fixtures**: a test asks for one by naming it as a parameter |

### What we built test-first
`tools/commit_msg.py` checks that each commit message starts with `JAR-<number>: <description>`.

1. **RED**: we wrote `tools/tests/test_commit_msg.py` first: valid examples, git's own merge and revert messages,
   nine invalid examples, comment-line handling, and the exit codes of `main()`. Running `uv run pytest` failed
   with `ModuleNotFoundError: No module named 'tools.commit_msg'`, which is correct: the code didn't exist yet.
2. **GREEN**: we wrote the smallest implementation that passes all 20 tests.
3. **REFACTOR**: nothing needed yet; Ruff and Pyright (strict) were already clean.

Notice that the tests describe *behaviour* ("rejects a lower-case key", "accepts git's merge messages"),
not *how* the code works. That's what lets you refactor safely later.

### The regular expression
```python
JIRA_KEY_PATTERN = re.compile(r"^JAR-\d+: \S")
```
| Part | Meaning |
|------|---------|
| `r"..."` | raw string: backslashes are passed to the regex engine unchanged |
| `^` | at the start of the text |
| `JAR-` | the literal characters `JAR-` |
| `\d+` | one or more digits |
| `: ` | a colon and a space |
| `\S` | one non-whitespace character, so the description isn't empty |

### Exit codes
A program tells its caller "success" or "failure" with a number: `0` = success, anything else = failure.
Git runs our hook and **aborts the commit if the exit code isn't 0**. We return `1` for a bad message and `2`
for wrong usage (no file given).

### `if __name__ == "__main__":`
Python sets `__name__` to `"__main__"` only when the file is run directly
(`python -m tools.commit_msg ...`), not when it's imported by the tests. It's Python's equivalent of
`public static void main(String[] args)`.

---

## 5. Git hooks and pre-commit

A **git hook** is a script git runs automatically at certain moments. Two matter here:
* `pre-commit`: runs before a commit is created. If it fails, there is no commit.
* `commit-msg`: runs after you type the message, receiving the message file's path. If it fails, there is no commit.

**pre-commit** (the tool) manages hooks from one file, `.pre-commit-config.yaml`, so every clone runs the same checks:

| Hook | What it prevents |
|------|------------------|
| trailing-whitespace, end-of-file-fixer | Noise in diffs |
| check-yaml, check-toml | Broken config files |
| check-merge-conflict | Committing `<<<<<<<` markers |
| check-added-large-files | Accidentally committing big files (models, datasets) |
| detect-private-key | Committing a private key |
| no-commit-to-branch | Committing directly on `dev`, `test`, `prod` |
| ruff-check, ruff-format | Lint errors and unformatted code |
| pyright | Type errors |
| jira-commit-message | Messages without `JAR-<n>:` (our own `tools/commit_msg.py`) |

```bash
uv run pre-commit install             # once per clone: writes the hooks into .git/hooks
uv run pre-commit run --all-files     # run every check on every file now
```
Hooks are the **local** safety net (fast feedback before you push). CI (JAR-3) is the **shared** safety net that
nobody can skip.

---

## 6. Repository hygiene files

| File | Purpose |
|------|---------|
| `.gitignore` | Files Git must never track: `.env` (secrets), `.venv/`, caches, `node_modules/`, AI model files |
| `.gitattributes` | Store text files with LF line endings. Windows writes CRLF, Linux writes LF; without this, every line can look changed. This fixes the `LF will be replaced by CRLF` warning we saw when creating the repo |
| `.editorconfig` | Same indentation, charset and line endings in every editor |
| `.env.example` | The *names* of required settings, without values. Real values go in `.env`, which is ignored. Same idea as SplitMate's `DB_PASSWORD` environment variable |
| `.vscode/extensions.json` | VS Code suggests the right extensions (Ruff, Python, EditorConfig) |

---

## 7. Process documents

* **CONTRIBUTING.md**: the SplitMate rules (Jira-first, TDD, naming, Definition of Done) plus the dev -> test ->
  prod promotion flow and releases.
* **Pull request template** (`.github/pull_request_template.md`): GitHub fills every new PR with the Definition
  of Done checklist, so self-review is never skipped.
* **ADR (Architecture Decision Record)**: a short file per significant decision: context, options, decision,
  consequences. Months later, it answers "why did we do it this way?". ADR-0001 records Expo vs Flutter.

---

## 8. Commands cheat-sheet

```bash
git switch dev && git pull                       # start from the latest dev
git switch -c feature/JAR-<n>-<description>      # new branch for an issue
uv sync                                          # install exact tool versions
uv run pytest                                    # tests
uv run ruff check . && uv run ruff format --check . && uv run pyright
uv run pre-commit run --all-files
git add <files> && git commit -m "JAR-<n>: <message>"
git push -u origin feature/JAR-<n>-<description>
gh pr create --base dev                          # open the pull request
```

## 9. Interview questions you can now answer
1. What is a virtual environment and why does Python need one when Java doesn't?
2. What's the difference between `pyproject.toml` and `uv.lock`? Which do you commit?
3. Linter vs formatter vs type checker: what does each catch?
4. Python is dynamically typed: what do type hints change at runtime? (Nothing. Tools like Pyright use them.)
5. Explain RED-GREEN-REFACTOR with an example you've built.
6. What is a git hook? Why have both pre-commit hooks and CI?
7. Why `.gitattributes` with `eol=lf` on a Windows machine?
8. What is an ADR and when do you write one?

## 10. Mistakes and lessons
* Running `uv run pytest` before the module existed gave `ModuleNotFoundError`. In TDD that's the expected
  RED step, not a problem.
