---
name: atlas-commit-message-writer
description: Use when the user asks to write, improve, review, or create a commit message for Atlas workspace changes, or asks to commit code/doc changes. This skill inspects the actual staged or working diff, respects Atlas repository boundaries, generates an accurate commit message, and only commits when the user explicitly asks.
metadata:
  short-description: Write Atlas commit messages from real diffs
---

# Atlas Commit Message Writer

Use this skill for commit-message writing and commit execution in the Atlas workspace.

## Repository Boundaries

The workspace contains separate repositories:

- Root repository: AI docs and workspace files such as `atlas-ai-docs/`
- `atlas/`: Atlas product code
- `atlas-test/`: E2E test framework and test cases
- `atlas-studio/`: frontend repository

Never mix staging, status, diff, or commits across repositories.

When the target repository is unclear, inspect the relevant git status first and choose the repository that contains the requested changes. If multiple repositories have relevant changes, handle them as separate commits.

## Commit Policy

- For `atlas/` and `atlas-test/`, do not commit unless the user explicitly asks to commit.
- For root `atlas-ai-docs/`, stable documentation updates may be committed when appropriate.
- Always base the message on the actual diff, preferably staged diff.
- If staged diff is empty, inspect working diff and either:
  - generate a suggested message for the working diff, or
  - stage only the files explicitly relevant to the user's request when the user asked to commit.
- Do not include unrelated files in the commit.
- Never delete files as part of this skill.

## Workflow

1. Identify the target repository.
2. Inspect `git status --short`.
3. Inspect staged diff with `git diff --cached --stat` and, when needed, `git diff --cached`.
4. If staged diff is empty and the user asked to commit, inspect working diff and stage only relevant files.
5. Generate a commit message from the actual changes.
6. If committing, run the commit in the target repository only.
7. Report the commit hash and message.

## Commit Message Structure

Use this structure. Separate the subject, body, and footer with blank lines:

```text
type(scope): Subject based on actual changes

Change point one.
Change point two.
Change point three.

Related to: 8-char commit sha, issue ID
Tested: Natural-language summary of verified cases
BREAKING CHANGE: Description of incompatible behavior change
```

The body is optional. The footer is optional. The final git commit message should use one of the accepted type prefixes.

## Commit Types

Prefer these types:

- `fix`: bug fixes, behavior corrections, P0/P1 regressions
- `feat`: new user-visible capability
- `docs`: documentation-only changes
- `test`: tests or test framework changes
- `refactor`: internal restructuring without behavior change
- `perf`: performance improvement
- `build`: build system, dependency, or CI changes
- `chore`: maintenance with no product behavior change

Use scope when it clarifies the affected area:

```text
fix(truncate): Restore sync lifecycle guards
docs(truncate): Record query meta propagation plan
test(store): Cover truncate graph failure propagation
```

## Subject Rules

- Base the subject on what actually changed in the diff.
- 50-72 characters max when practical.
- Imperative mood: use `add`, `fix`, `restore`, `make`, not `added`, `fixed`, `restores`.
- Capitalize the first letter after the type/scope when using a sentence-like subject, unless the existing repo style is lower-case.
- No period at the end.
- Be specific about the changed behavior.
- Avoid vague subjects like `update code`, `fix issue`, or `misc changes`.

Good:

```text
fix(truncate): Make graph truncate synchronous
```

Also acceptable for local repo style:

```text
fix truncate sync P0 regressions
```

Bad:

```text
fixed truncate
update files
changes for review
```

## Body Rules

Add a body only when the subject cannot carry the details.

The body must list concrete change points from the actual diff:

- one change point per line
- no wrapping inside the body; keep each change point on a single line
- no blank lines between body change points
- no general project background unless it is needed to understand the change
- no speculative impact that is not visible from the diff or user-confirmed context

Example:

```text
fix(truncate): Make graph truncate synchronous

Wait for all label truncate futures before truncate_graph returns.
Restore write_flag and index-state checks before label truncate.
Pass graph query_meta through store truncate handlers without store-side commit.
```

## Footer Rules

Use a footer for related commit or issue metadata, or incompatible behavior changes. The footer must be separated from the body by a blank line.

Footer entries may include:

- related 8-character commit SHAs
- issue IDs or task IDs
- `Tested:` entries summarizing actual verification that was run
- `BREAKING CHANGE:` entries

Only write `Tested:` when there is real self-test coverage from this change. The value should summarize the verified cases or scenarios in natural language, not list the exact shell command. If no self-test covered the change, omit `Tested:` entirely.

Examples:

```text
feat(api): Change user endpoint response format

Update the user response serializer.
Rename the response identifier field.

Related to: cbe8e421, AG-4057
Tested: Verified suite compilation without running service cases
BREAKING CHANGE: User API now returns `userId` instead of `id`
```

Only add `BREAKING CHANGE:` when callers, stored data, APIs, CLI behavior, config, or compatibility are intentionally broken.

## Output Modes

When the user asks for a recommendation only, output 1-3 candidate messages.

When the user asks to commit, commit with the best message and report:

- target repository
- commit hash
- subject
- verification already known, if relevant

## Safety Checks

Before committing, confirm:

- staged files belong to only one repository
- staged files match the user's requested task
- no unrelated generated files are included
- no deletion commands are needed
