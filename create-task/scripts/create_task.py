#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
from datetime import date
from pathlib import Path


DIRECTORY_GUIDE = """- `context/`: project background, system assumptions, glossary, architecture, and research notes.
- `tasks/`: active work, backlog items, and key decisions.
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

- Define the first useful scope and success criteria.
- Research the minimum viable workflow and core constraints.
- Build a lightweight project plan that can guide implementation.

## Initial Scope

- Start with a small, reviewable first version.
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
- MVP: the smallest version that can validate the core workflow.
- Signal: evidence that helps decide what to build or change next.
- Review loop: the process of checking outputs and improving the workflow.
""",
        "tasks/active.md": f"""# Active Tasks

## In Progress

- [ ] Task: {active_goal}
  Owner: {owner}
  Next step: Define the first workflow, required inputs, output shape, and validation criteria

## Blocked

- None

## Recently Completed

- [x] Initialized the {title} project directory
""",
        "tasks/backlog.md": f"""# Backlog

- [ ] Define the first workflow
  Priority: High
  Notes: Identify the smallest useful input-process-output loop

- [ ] Define the output schema
  Priority: High
  Notes: Make results easy to inspect, compare, and improve

- [ ] Research comparable tools or workflows
  Priority: Medium
  Notes: Extract patterns worth borrowing and risks to avoid

- [ ] Decide the first implementation shape
  Priority: Medium
  Notes: Compare document-only, script, CLI, local web app, or hosted app options
""",
        "tasks/decisions.md": f"""# Decisions

## Decision Log

### {today}

- Decision: Manage {title} as a separate project.
- Reason: The work has its own context, tasks, decisions, and implementation path.
- Impact: Related materials will be maintained under `{dir_name}/`.
""",
        "logs/worklog.md": f"""# Work Log

## {today}

- Created `{dir_name}/` from `project-template/`.
- Initialized project documentation for {description}.
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
