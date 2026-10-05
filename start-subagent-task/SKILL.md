---
name: start-subagent-task
description: Discuss, document, launch, and monitor a branch-isolated Codex subagent coding task for later main-agent review and integration. Use when the user asks to start, delegate, parallelize, or run code work with subagents, including tasks with overlapping write sets that must proceed concurrently in separate tmp/ worktrees and be reconciled by the main agent.
---

# Start Subagent Task

Use a review-first workflow. The main agent owns planning, canonical documentation, delegation, review, and integration. The subagent owns only the frozen implementation task.

Main-agent acceptance has two mandatory phases:

1. static review in the isolated worktree;
2. integration validation in the target repository after pick and conflict resolution.

Do not repeat compilation or tests during static review. The target repository's
combined build and tests are the authoritative acceptance run.

## Hard Gates

Do not spawn a coding subagent until:

1. Scope, implementation plan, and test plan have been discussed with the user.
2. The user has agreed to all material decisions.
3. A parent project exists at the workspace root using the `YYYY-MM-DD-*` layout.
4. Requirements, non-goals, write set, tests, acceptance criteria, and stop conditions are frozen.
5. Active-agent write sets have been checked and any overlap has been recorded
   with an integration order and main-agent conflict owner.
6. The preparation script has created the canonical subtask record and isolated worktree.

If any gate is incomplete, continue discussion or documentation. Do not spawn early.

## Decide Whether To Delegate

Delegate only a bounded task with frozen behavior and independently reviewable
acceptance criteria.

Keep work in the main agent when:

- the next main-thread action depends immediately on the result;
- architecture or semantics remain disputed;
- the task requires frequent user decisions;
- the task depends on uncommitted behavior from another agent and cannot start
  correctly from the documented committed baseline.

Overlapping write sets are allowed when parallel progress is worth later merge
work. Every task uses a unique branch and worktree. The main agent owns
cherry-pick order, conflict resolution, and combined tests; child agents do not
coordinate edits across worktrees.

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

Read `<parent-task>/tasks/subagents/README.md` when present. Compare repository and allowed write sets for every state that is not `accepted` or `failed`.

- Prefer disjoint write sets when decomposition remains natural.
- Do not reject a task solely because its write set overlaps active work.
- Record each overlapping agent/subtask and the expected integration order.
- Use the same committed baseline for independent parallel changes. Serialize
  tasks only when one requires another task's uncommitted behavior.
- Worktree isolation prevents concurrent filesystem edits but does not remove
  textual or semantic merge conflicts.
- Record the planned task before spawning.
- Do not start more agents than the configured capacity.

## Prepare Deterministically

Run `scripts/prepare_subagent_task.py` from this skill after all gates pass.

First use `--dry-run`, inspect the resolved paths, baseline, branch mode, and generated worktree command, then run without `--dry-run`.

Example:

```powershell
python <skill-dir>\scripts\prepare_subagent_task.py `
  --workspace-root E:\projects\project-manager `
  --repository stock-harness `
  --parent-task 2026-07-27-stock-harness `
  --slug <subtask-slug> `
  --title "<title>" `
  --baseline <commit> `
  --suffix <stable-unique-suffix> `
  --overlap-with "<agent-or-subtask>" `
  --integration-order "pick after <agent-or-subtask>" `
  --requirement "<requirement>" `
  --non-goal "<non-goal>" `
  --write-path "src/path" `
  --plan-step "<implementation step>" `
  --test "<test>" `
  --acceptance "<acceptance criterion>" `
  --stop-condition "<condition requiring input>" `
  --dry-run
```

Repeat list options as needed. Generate one unique suffix and reuse it for the
dry-run and real preparation call.

The script:

- validates workspace, repository, parent task, baseline, slug, repository-relative
  write paths, root `tmp/` ignore coverage, and collisions;
- creates `<parent-task>/tasks/subagents/<slug>/README.md`;
- maintains `<parent-task>/tasks/subagents/README.md`;
- creates `<workspace-root>/tmp/subagents/<repo>-<slug>-<suffix>/`;
- creates the code worktree in its `worktree/` child;
- creates sibling `status.md`, `metadata.json`, and `prompt.md`;
- creates a unique temporary branch for every worktree, using
  `codex/subagent/<slug>-<suffix>` unless `--branch` is supplied;
- records overlapping agents/tasks and the intended integration order;
- never deletes, cleans, commits, merges, or pushes.

The root repository must ignore `tmp/`. Stop if it does not.

Follow repository dangerous-command confirmation rules before worktree creation. Never reuse a runtime path, task directory, worktree, or branch.

## Ownership Boundaries

The main agent writes canonical files under the selected workspace project directory.

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

Overlapping children follow the same rules. A child must not inspect another
child's worktree or attempt cross-task conflict resolution.

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
static-reviewed
integrating
accepted
```

Use these checkpoints:

1. `prepared`: worktree and runtime records exist at the frozen baseline.
2. `inspected`: relevant code paths were checked and the plan remains valid.
3. `implemented`: scoped edits are complete.
4. `tested`: agreed tests ran and exact results are recorded.
5. `ready-for-review`: diff and residual risks are summarized without a commit.

A completed agent turn does not imply accepted or integrated code.

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

## Two-Phase Acceptance

When the subagent reaches `ready-for-review`:

### Phase 1: Static Worktree Review

1. Confirm there is no subagent commit.
2. Inspect status and the complete worktree diff.
3. Check the diff against write scope and non-goals.
4. Check generated files, lockfiles, formatting, and repository rules.
5. Review correctness, compatibility, performance, test design, and missing tests.
6. Read the subagent's recorded test evidence, but do not independently compile
   or rerun tests in the worktree.
7. Set `changes-requested` or `static-reviewed`.
8. Record findings, accepted risks, required integration order, and planned
   target-repository test commands in canonical documentation.

Static review is not final acceptance. It establishes that the diff is eligible
for integration. Avoiding an independent worktree build prevents repeated
compilation and does not weaken final validation because Phase 2 is mandatory.

### Phase 2: Target-Repository Integration Validation

After every selected subtask is `static-reviewed`:

1. Obtain required commit and integration approval.
2. Create one reviewed commit on each child branch.
3. Pick commits into the target repository in documented order.
4. Resolve textual and semantic conflicts in the target repository.
5. Check the complete combined diff and repository rules.
6. Compile and run focused plus combined unit tests once in the target
   repository. Do not return to child worktrees for duplicate validation.
7. Fix integration-only defects in the target repository and rerun only the
   affected commands.
8. Set `accepted` only after the target-repository build and required tests pass.
9. Record child commit ids, integrated commit ids, conflicts, resolutions,
   commands, and exact results in canonical documentation.

Do not integrate automatically. The main agent or user decides whether to revise, commit, or integrate.

## Integrate Branches

After branch-isolated tasks are `static-reviewed`:

1. Document the cherry-pick order. Prefer foundational changes before
   dependent behavior changes.
2. Obtain the repository's required commit and integration approval.
3. Create one reviewed commit on each static-reviewed child branch. Child agents do
   not create these commits before review.
4. Set the subtasks to `integrating`, then cherry-pick commits into the target
   branch one at a time.
5. Resolve textual and semantic conflicts in the target worktree. Preserve
   both tasks' acceptance criteria instead of choosing conflict sides
   mechanically.
6. Prefer one combined compilation and test run after all picks. Run an
   intermediate test only when conflict resolution creates a specific,
   otherwise hard-to-isolate correctness risk.
7. Complete Phase 2 integration validation before marking any picked task
   `accepted`.

If commit creation is not authorized, apply reviewed patches sequentially in
the target worktree instead. Do not use rebase or force-push as an integration
shortcut.

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
- overlapping tasks and planned integration order;
- changed files;
- tests and results;
- blockers and residual risks;
- Phase 1 static-review result;
- Phase 2 integration build and test result;
- commit status, which must be `not committed` before review;
- recommended integration and cleanup actions.
