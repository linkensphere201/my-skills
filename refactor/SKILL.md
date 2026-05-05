---
name: refactor
description: Use when the user asks Codex to refactor code and provides, or should provide, a refactor target plus a rough approach. Use especially when the user wants a draft plan before edits, explicit confirmation before implementation, plan-driven execution, and related tests added or updated.
---

# Refactor

## Overview

Use this skill to turn a refactor request into a controlled engineering workflow: understand the target, draft a concrete plan, wait for user confirmation, then implement in small steps with tests.

## Required Input

Prefer these two fields:

```text
Refactor target:
Rough approach:
```

If either field is missing, infer it from the conversation when low risk. Ask one concise clarification only when the target or approach is too ambiguous to plan safely.

## Workflow

### 1. Draft Before Editing

Before making code changes:

- Read the relevant code, tests, and local project rules.
- Identify current behavior and the reason the refactor is needed.
- Produce a draft plan covering:
  - scope and non-scope
  - proposed design
  - files or modules likely to change
  - behavior-preservation expectations
  - new or updated tests
  - risks and rollback points
- Ask the user to confirm the plan before editing.

Do not edit implementation files before the user confirms, unless the user explicitly says to skip confirmation.

### 2. Execute With A Plan

After confirmation:

- Create or maintain a short checklist with one active step at a time.
- Make small, reversible changes.
- Preserve user-authored and unrelated work.
- Keep public behavior stable unless the refactor target explicitly changes behavior.
- Prefer existing local patterns over new abstractions.
- Avoid broad rewrites when a narrow structural change solves the problem.

### 3. Test The Refactor

Add or update tests proportional to risk:

- Add focused unit tests for new boundaries, runners, adapters, or extracted helpers.
- Add regression tests for behavior that must remain unchanged.
- Add failure-path tests when the refactor changes setup, config, auth, IO, or orchestration.
- Run the narrowest relevant tests first, then broader tests when the touched surface is shared.

If tests cannot be run, state why and describe the residual risk.

### 4. Report

Finish with:

- what changed
- why the new structure matches the confirmed plan
- tests run and result
- remaining risks or follow-up work

Keep the final report concise and include file references when useful.

## Confirmation Gate

The default confirmation prompt should be short:

```text
确认这个方案后我再开始改代码。
```

If the user replies with an explicit approval such as "可以", "确认", "按这个做", or equivalent, proceed with implementation.
