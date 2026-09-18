---
name: export-task-ai-docs
description: Convert an Atlas task record into a verified, English, AI-readable feature documentation set under the owning project's doc directory. Use when the user asks to export, consolidate, publish, or reorganize a task from atlas-ai-docs/tasks into project documentation covering requirements, design, implementation, testing, usage, operations, and review conclusions for each delivery stage.
---

# Export Task AI Docs

Turn task history into durable project documentation. Treat current code and test evidence as implementation truth, while preserving confirmed product decisions and clearly labeling gaps or deferred work.

Read [references/document-contract.md](references/document-contract.md) before writing the output files.

## Inputs

Accept a task name, task directory, task document path, or unambiguous task description.

Also accept these optional inputs:

- target project repository;
- target documentation directory;
- feature branch and base branch;
- commit or release scope;
- requested optional documents.

Resolve an omitted task path from `atlas-ai-docs/tasks/`. Resolve an omitted target repository from the task's implementation ownership and repository references. Ask the user only when multiple tasks or owning repositories remain plausible after inspection.

## Workflow

### 1. Resolve the task and repository boundaries

1. Match an exact task directory or path first.
2. Fall back to `atlas-ai-docs/tasks.md`, aliases, and a unique name fragment.
3. Read `WORKSPACE_STRUCTURE.md` and the applicable `AGENTS.md` files.
4. Keep root documentation, product code, and test repositories separate in all Git operations.
5. Record the target repository, current branch, base branch, relevant commits, and worktree state.

Do not modify product code, tests, task records, or unrelated documentation as part of this export unless the user explicitly asks.

### 2. Build an evidence inventory

Inspect the task `README.md` and relevant requirement, plan, design, handoff, implementation, test, review, and usage files. Then verify their claims against the target branch:

- source code and generated schema sources;
- unit and integration tests;
- external E2E repository tests;
- Git history and the feature diff from the base branch;
- existing project documentation conventions;
- recorded test commands, dates, commits, and results.

Read the smallest useful file set first, then expand when a claim crosses module or repository boundaries. Do not treat conversation summaries or old handoff files as proof of current behavior.

### 3. Reconcile sources

Use the following authority rules:

- Current user direction and confirmed task decisions define intended scope.
- Current source code defines implemented behavior.
- Tests and captured results define demonstrated behavior only for their recorded revision and environment.
- Git history defines branch and commit provenance.
- Older plans and handoffs provide context, not current-state proof.

When sources conflict, report the drift in the relevant review document. Classify the item as implemented, deferred, obsolete, unverified, or an open issue. Never silently rewrite intent to match code.

### 4. Choose the target directory

Inspect the project's existing `doc/` or equivalent directory before choosing names.

- Follow an established feature-directory and numbering convention when one exists.
- Otherwise use a concise feature directory such as `doc/<feature-name>/`.
- Reuse an existing feature directory only when it clearly owns the same feature.
- Do not overwrite unrelated files.
- Use relative links within the document set and repository-relative source paths in prose.

### 5. Write the document set

Write all prose in English. Preserve non-English text only when it is a required identifier, literal error, syntax token, or cited external name.

Create the mandatory overview and four stage documents with a separate review for each stage:

- overview/index;
- requirements and requirements review;
- design and design review;
- implementation and implementation review;
- testing and testing review.

Add usage and release-operations documents when the feature has user-facing syntax, APIs, permissions, persistence, upgrade, rollback, deployment, or compatibility concerns. Follow the exact content contract in the reference file.

Prefer diagrams in Mermaid when they materially clarify ownership or execution flow and the target documentation already permits Mermaid. Keep diagrams consistent with the code; omit them when they would only restate prose.

### 6. Validate the result

Check all of the following before reporting completion:

1. Every supported and unsupported behavior is grounded in current evidence.
2. Every review finding has severity, disposition, and evidence or rationale.
3. Test results include command, revision, environment, and outcome when known.
4. Tests that were not run are explicitly marked as not run.
5. Internal links are relative and resolve to files in the output set.
6. Source references use repository-relative paths and valid identifiers.
7. English prose contains no accidental untranslated task notes.
8. The output contains no unfinished placeholders or unsupported release claims.
9. Formatting and whitespace checks pass.
10. Git status shows only the intended documentation changes in the target repository.

Run lightweight documentation checks appropriate to the repository. Do not run expensive builds or E2E suites merely to write documentation unless the user requested fresh verification; instead preserve and qualify existing evidence.

## Reporting

Return:

- the target documentation directory;
- the files created or updated;
- the branch and commit scope documented;
- validation performed;
- unresolved drift, unverified claims, and remaining release risks.

Do not commit or push the target repository unless the user explicitly asks.
