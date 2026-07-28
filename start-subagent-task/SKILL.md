---
name: start-subagent-task
description: Discuss, document, launch, and monitor an isolated Codex subagent coding task for later main-agent review. Use when the user asks to start, delegate, parallelize, or run code work with a subagent or multi-agent workflow, especially when work must use an ignored workspace tmp/ worktree, have explicit scope and tests, report checkpoints, stop on blockers, and remain uncommitted until the main agent reviews it.
---

# Start Subagent Task

Use a review-first workflow. The main agent owns planning, canonical documentation, delegation, review, and integration. The subagent owns only the frozen implementation task.

## Hard Gates

Do not spawn a coding subagent until:

1. Scope, implementation plan, and test plan have been discussed with the user.
2. The user has agreed to all material decisions.
3. A parent task exists under `atlas-ai-docs/tasks/`.
4. Requirements, non-goals, write set, tests, acceptance criteria, and stop conditions are frozen.
5. Active-agent write sets have been checked for conflicts.
6. The preparation script has created the canonical subtask record and isolated worktree.

If any gate is incomplete, continue discussion or documentation. Do not spawn early.

## Decide Whether To Delegate

Delegate only a bounded task that can proceed while the main agent does non-overlapping work.

Keep work in the main agent when:

- the next main-thread action depends immediately on the result;
- architecture or semantics remain disputed;
- another active agent modifies the same files;
- the task requires frequent user decisions;
- the task cannot be assigned a disjoint write set.

Never spawn agents merely to consume available concurrency. The configured maximum is a ceiling, not a target.

## Freeze The Task

Agree with the user on:

- objective and observable behavior;
- repository and exact committed baseline;
- allowed and forbidden files;
- compatibility and fallback behavior;
- implementation steps;
- unit, integration, and end-to-end tests;
- non-goals and deferred work;
- acceptance criteria;
- conditions that require stopping for input.

Summarize the agreement before preparation. Do not reinterpret it in the child prompt.

## Check Active Work

Read `<parent-task>/subagents/README.md` when present. Compare repository and allowed write sets for every state that is not `accepted` or `failed`.

- Reject overlapping write sets by default.
- Serialize explicitly coupled tasks instead of relying on merge conflict resolution.
- Record the planned task before spawning.
- Do not start more agents than the configured capacity.

## Prepare Deterministically

Run `scripts/prepare_subagent_task.py` from this skill after all gates pass.

First use `--dry-run`, inspect the resolved paths, baseline, branch mode, and generated worktree command, then run without `--dry-run`.

Example:

```bash
python3 <skill-dir>/scripts/prepare_subagent_task.py \
  --workspace-root <workspace-root> \
  --repository atlas \
  --parent-task atlas-ai-docs/tasks/YYYY-MM-DD-<task> \
  --slug <subtask-slug> \
  --title "<title>" \
  --baseline <commit> \
  --requirement "<requirement>" \
  --non-goal "<non-goal>" \
  --write-path "src/path" \
  --plan-step "<implementation step>" \
  --test "<test>" \
  --acceptance "<acceptance criterion>" \
  --stop-condition "<condition requiring input>" \
  --dry-run
```

Repeat list options as needed.

The script:

- validates workspace, repository, parent task, baseline, slug, repository-relative
  write paths, root `tmp/` ignore coverage, and collisions;
- creates `<parent-task>/subagents/<slug>/README.md`;
- maintains `<parent-task>/subagents/README.md`;
- creates `<workspace-root>/tmp/subagents/<repo>-<slug>-<suffix>/`;
- creates the code worktree in its `worktree/` child;
- creates sibling `status.md`, `metadata.json`, and `prompt.md`;
- creates a detached worktree by default;
- creates a temporary branch only with an explicitly agreed `--branch`;
- never deletes, cleans, commits, merges, or pushes.

The root repository must ignore `tmp/`. Stop if it does not.

Follow repository dangerous-command confirmation rules before worktree creation. Never reuse a runtime path, task directory, worktree, or branch.

## Ownership Boundaries

The main agent writes canonical files under `atlas-ai-docs/`.

The subagent may write only:

- documented code paths inside its assigned worktree;
- the generated runtime `status.md` beside the worktree.

The subagent must not edit the root task repository. The main agent reads runtime status and synchronizes durable checkpoint, blocker, finding, and review information into the canonical subtask record.

## Spawn The Agent

Read the generated `prompt.md` and include it in a self-contained spawn request. Also provide:

- repository-specific safety rules;
- generated-file and lockfile rules;
- exact test commands when known;
- final response contract.

Require the subagent to:

- work only in the assigned worktree;
- never commit, merge, rebase, cherry-pick, push, remove files, or clean;
- inspect current code before editing;
- update runtime `status.md` at every checkpoint;
- record exact tests and results;
- stop at unresolved semantic, scope, safety, or environment blockers;
- leave changes dirty for main-agent review;
- finish at `ready-for-review`, not `accepted`.

Record the returned agent ID and nickname in the canonical task record and active-agent registry.

## Lifecycle And Checkpoints

Use these lifecycle states:

```text
planned
running
blocked
failed
ready-for-review
changes-requested
reviewed
accepted
```

Use these checkpoints:

1. `prepared`: worktree and runtime records exist at the frozen baseline.
2. `inspected`: relevant code paths were checked and the plan remains valid.
3. `implemented`: scoped edits are complete.
4. `tested`: agreed tests ran and exact results are recorded.
5. `ready-for-review`: diff and residual risks are summarized without a commit.

A completed agent turn does not imply accepted code.

## Monitor Without Blocking

Use checkpoint progress, not repeated blocking waits or invented percentages.

- Continue meaningful, non-overlapping main-agent work.
- Treat runtime `status.md` as the live source.
- Synchronize changed checkpoints into the canonical task record.
- Report concise checkpoint changes to the user.
- Query agent status sparingly and on user request.
- Use intermediate agent messages when supported.
- For long tasks, require status updates after each file group or test phase, not arbitrary time estimates.

## Handle Blockers

The subagent must set state to `blocked` and record:

```text
checkpoint:
blocking condition:
evidence:
decision needed:
safe state of worktree:
```

It then stops without speculative edits.

The main agent:

1. synchronizes the blocker into canonical documentation;
2. resolves it from the frozen plan when possible;
3. asks the user when a material decision remains;
4. resumes the same agent after resolution;
5. does not spawn a replacement for the same task.

## Review

When the subagent reaches `ready-for-review`:

1. Confirm there is no subagent commit.
2. Inspect status and the complete worktree diff.
3. Check the diff against write scope and non-goals.
4. Check generated files, lockfiles, formatting, and repository rules.
5. Re-run risk-appropriate tests independently.
6. Review correctness, compatibility, performance, and missing tests.
7. Set `changes-requested`, `reviewed`, or `accepted`.
8. Write the review into canonical documentation.

Do not integrate automatically. The main agent or user decides whether to revise, commit, or integrate.

## Cleanup Handoff

At final review, record:

- integration state;
- whether the runtime directory and worktree should be retained;
- whether an optional temporary branch exists;
- exact proposed cleanup commands.

Never perform cleanup automatically. Follow workspace confirmation rules before any removal.

## Completion Report

Report:

- agent ID and lifecycle state;
- runtime directory, worktree, and branch mode;
- changed files;
- tests and results;
- blockers and residual risks;
- main-agent review result;
- commit status, which must be `not committed` before review;
- recommended integration and cleanup actions.
