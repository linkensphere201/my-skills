#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
from datetime import date
from pathlib import Path


DIRECTORY_GUIDE = """- `context/`: project background, system assumptions, glossary, architecture, and research notes.
- `tasks/`: milestone register, numbered active work, backlog items, and key decisions.
- `prompts/`: reusable prompts.
- `logs/`: chronological project work notes."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a project-manager task directory from project-template.")
    parser.add_argument("project_name", help="Project/task name, for example ai-log-analyzer.")
    parser.add_argument("--description", default="TODO", help="One-line project description.")
    parser.add_argument("--goal", default=None, help="Optional first active goal.")
    parser.add_argument("--project-root", default=".", help="Workspace root containing project-template.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Date prefix in YYYY-MM-DD format.")
    parser.add_argument("--owner", default="hp + Codex", help="Owner value for tasks/active.md.")
    parser.add_argument("--no-index", action="store_true", help="Create the project without updating root indexes.")
    return parser.parse_args()


def slugify(text: str) -> str:
    text = text.strip().lower().replace("_", "-").replace(" ", "-")
    text = re.sub(r"[^a-z0-9-]", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def titleize(slug: str) -> str:
    words = []
    for part in slug.split("-"):
        if part.lower() in {"ai", "api", "llm", "ui", "ux"}:
            words.append(part.upper())
        else:
            words.append(part.capitalize())
    return " ".join(words)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def build_docs(title: str, dir_name: str, description: str, active_goal: str, owner: str, today: str) -> dict[str, str]:
    return {
        "README.md": f"""# {title}

This project is for {description}.

## Current Goals

- Classify the project as simple or complex and approve the milestone plan.
- Define the first useful scope and success criteria using stable milestone and task IDs.
- Research the minimum viable workflow and core constraints.
- Build a lightweight project plan that can guide implementation.

## Initial Scope

- Start with a small, reviewable first version.
- For complex work, define the complete known `M1` through `Mn` sequence before implementation.
- Keep the project self-contained inside `{dir_name}/`.
- Record stable background in `context/` and active status in `tasks/`.

## Non-Goals

- Do not overbuild before the first workflow is validated.
- Do not mix this project's documents with other project directories.
- Do not hide assumptions or unresolved questions.

## Directory Guide

{DIRECTORY_GUIDE}
""",
        "context/project-overview.md": f"""# Project Overview

## Background

This project tracks the work for {description}.

The first phase should clarify the problem, define a minimum useful workflow, and identify the constraints that matter before implementation.

## Goals

- Clarify the target user and use case.
- Define the first version scope.
- Identify required inputs, outputs, and quality checks.
- Produce an implementation-ready plan.

## Non-Goals

- Do not solve adjacent projects in this directory.
- Do not assume the first version needs every future feature.
- Do not treat early ideas as validated requirements.

## Key Questions

- Is this project simple or complex?
- What are the complete known milestones `M1` through `Mn`?
- What is the smallest useful version of this project?
- Which inputs and outputs are required for the first workflow?
- What risks or constraints need to be handled early?
- What should be measured to decide whether the first version works?
""",
        "context/research-notes.md": f"""# Research Notes

## Initial Observations

- The project should start with a narrow, testable workflow.
- Early notes should distinguish facts, assumptions, open questions, and recommendations.
- Research should produce implementation guidance, not only background reading.

## Candidate Research Areas

- Target users and concrete usage scenarios.
- Existing tools or comparable workflows.
- Data, integration, or environment constraints.
- Risks, edge cases, and validation methods.

## Open Questions

- What is the first workflow to prototype?
- Which existing tools should be studied first?
- What assumptions need validation before implementation?
""",
        "context/architecture.md": f"""# Architecture

## Initial System Concept

The architecture is not finalized yet. The first pass should describe the minimum workflow as a simple pipeline:

1. Input: define what the user or system provides.
2. Process: transform inputs into useful intermediate results.
3. Analyze: apply rules, models, or human review where needed.
4. Output: produce a result that is easy to inspect and act on.
5. Review: record outcomes and improve the workflow.

## First-Phase Principles

- Keep the first version small and observable.
- Prefer explicit data structures over hidden state.
- Preserve source evidence for important conclusions.
- Make manual review possible before automation expands.
""",
        "context/glossary.md": f"""# Glossary

- Project: the self-contained work tracked under `{dir_name}/`.
- Milestone ID: an immutable `M<n>` identifier for an independently acceptable delivery.
- Task ID: an immutable hierarchical identifier such as `M1.1` or `M1.1.1`.
- MVP: the smallest version that can validate the core workflow.
- Signal: evidence that helps decide what to build or change next.
- Review loop: the process of checking outputs and improving the workflow.
""",
        "tasks/milestones.md": f"""# Milestone Register

## Complexity

- Classification: Pending
- Planning gate: Pending

Complex projects must define the complete known milestone sequence `M1` through `Mn` and approve milestone acceptance targets before implementation begins.

## Numbering Contract

- `M<n>`: milestone.
- `M<n>.<s>`: stable subgoal or work package.
- `M<n>.<s>.<t>`: executable task.
- Add a fourth numeric level only when required.
- Never renumber or reuse an ID after implementation or progress reporting begins.
- Keep cancelled or superseded IDs and mark their final state.
- Reference the most specific applicable ID in every progress record.

## Milestones

| ID | Name | Goal | Acceptance target | Status |
|---|---|---|---|---|
| `M1` | First useful delivery | Define the first independently acceptable project outcome. | Define measurable acceptance before implementation. | Planning |

## Decomposition

### M1

- [ ] `M1.1` Define and approve the first milestone plan.
  - [ ] `M1.1.1` Classify the project and define the complete known milestone sequence.
  - [ ] `M1.1.2` Define milestone goals and acceptance targets.
  - [ ] `M1.1.3` Decompose the active milestone into executable tasks.
""",
        "tasks/active.md": f"""# Active Tasks

## In Progress

- [ ] `M1.1.1` {active_goal}
  Owner: {owner}
  Next step: Classify project complexity and define the complete known milestone sequence

## Blocked

- None

## Recently Completed

- [x] `M1` Initialized the {title} project directory and numbering contract
""",
        "tasks/backlog.md": f"""# Backlog

- [ ] `M1.1` Define and approve the milestone plan
  Priority: High
  Notes: Complex work must define `M1` through `Mn` before implementation

- [ ] `M1.1.2` Define milestone goals and acceptance targets
  Priority: High
  Notes: Make every milestone independently reviewable

- [ ] `M1.1.3` Decompose the active milestone into executable tasks
  Priority: High
  Notes: Use immutable hierarchical IDs such as `M1.2.1`

- [ ] `M1.2` Research comparable tools or workflows
  Priority: Medium
  Notes: Extract patterns worth borrowing and risks to avoid

- [ ] `M1.3` Decide the first implementation shape
  Priority: Medium
  Notes: Compare document-only, script, CLI, local web app, or hosted app options
""",
        "tasks/decisions.md": f"""# Decisions

## Decision Log

### {today}

- Decision [`M1`]: Manage {title} as a separate project.
- Reason: The work has its own context, tasks, decisions, and implementation path.
- Impact: Related materials will be maintained under `{dir_name}/`.
""",
        "logs/worklog.md": f"""# Work Log

## {today}

- [`M1`] Created `{dir_name}/` from `project-template/`.
- [`M1.1.1`] Initialized project documentation and the milestone planning gate for {description}.
""",
        "prompts/reusable-prompts.md": f"""# Reusable Prompts

## Project Review

```text
Review the following project plan.

Please identify:
1. Unclear scope
2. Missing assumptions
3. Main risks
4. Suggested next steps
5. A smaller MVP if the plan is too broad

Project plan:
[Paste project plan]
```
""",
    }


def insert_before_marker(text: str, marker: str, line_to_insert: str) -> str:
    if line_to_insert in text:
        return text
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if marker in line:
            lines.insert(index, line_to_insert)
            return "\n".join(lines) + "\n"
    if text and not text.endswith("\n"):
        text += "\n"
    return text + line_to_insert + "\n"


def update_indexes(project_root: Path, dir_name: str, description: str) -> None:
    readme = project_root / "README.md"
    if readme.exists():
        line = f"- `{dir_name}/`: {description}"
        text = readme.read_text(encoding="utf-8")
        text = insert_before_marker(text, "`project-template/`", line)
        write(readme, text)

    structure = project_root / "WORKSPACE-STRUCTURE.md"
    if structure.exists():
        row = f"| `{dir_name}/` | {description} |"
        text = structure.read_text(encoding="utf-8")
        text = insert_before_marker(text, "| `project-template/` |", row)
        write(structure, text)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    template_dir = project_root / "project-template"
    if not template_dir.exists():
        raise SystemExit(f"error: project-template not found: {template_dir}")

    slug = slugify(args.project_name)
    if not slug:
        raise SystemExit("error: project name normalized to empty slug")

    dir_name = f"{args.date}-{slug}"
    task_dir = project_root / dir_name
    if task_dir.exists():
        raise SystemExit(f"error: project directory already exists: {task_dir}")

    shutil.copytree(template_dir, task_dir)

    title = titleize(slug)
    description = args.description.strip() or "TODO"
    active_goal = args.goal.strip() if args.goal else f"Define the minimum viable plan for {title}"
    docs = build_docs(title, dir_name, description, active_goal, args.owner, args.date)
    for rel_path, content in docs.items():
        write(task_dir / rel_path, content)

    if not args.no_index:
        update_indexes(project_root, dir_name, description)

    print(f"created: {task_dir}")
    print(f"updated indexes: {'no' if args.no_index else 'yes'}")
    print(f"active task: {active_goal}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
