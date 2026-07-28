#!/usr/bin/env python3
"""Prepare documented, isolated subagent work without committing or deleting."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")


class PreparationError(RuntimeError):
    pass


def run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise PreparationError(f"git {' '.join(args)} failed: {detail}")
    return result


def resolve_from(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return (base / path).resolve() if not path.is_absolute() else path.resolve()


def require_under(path: Path, parent: Path, label: str) -> None:
    try:
        path.relative_to(parent)
    except ValueError as exc:
        raise PreparationError(f"{label} must be under {parent}: {path}") from exc


def markdown_list(items: Iterable[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def normalize_write_paths(items: Iterable[str], repository: Path) -> list[str]:
    normalized = []
    for item in items:
        path = Path(item)
        if path.is_absolute() or ".." in path.parts:
            raise PreparationError(f"--write-path must be repository-relative and may not contain '..': {item}")
        value = path.as_posix().strip("/")
        if not value or value == ".":
            raise PreparationError("--write-path may not select the entire repository")
        require_under((repository / value).resolve(), repository, "write path")
        normalized.append(value)
    return normalized


def parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(
        description="Create a subagent task record, runtime status, prompt, and git worktree.",
    )
    arg_parser.add_argument("--workspace-root", default=".", help="Atlas AI workspace root.")
    arg_parser.add_argument("--repository", required=True, help="Git repository path, absolute or workspace-relative.")
    arg_parser.add_argument("--parent-task", required=True, help="Parent task path, absolute or workspace-relative.")
    arg_parser.add_argument("--slug", required=True, help="Lowercase hyphenated subtask identifier.")
    arg_parser.add_argument("--title", required=True, help="Human-readable subtask title.")
    arg_parser.add_argument("--baseline", default="HEAD", help="Committed baseline ref.")
    arg_parser.add_argument("--suffix", help="Unique runtime suffix; defaults to a UTC timestamp.")
    arg_parser.add_argument("--branch", help="Optional temporary branch. Detached worktree is the default.")
    arg_parser.add_argument("--requirement", action="append", required=True)
    arg_parser.add_argument("--non-goal", action="append", required=True)
    arg_parser.add_argument("--write-path", action="append", required=True)
    arg_parser.add_argument("--plan-step", action="append", required=True)
    arg_parser.add_argument("--test", action="append", required=True)
    arg_parser.add_argument("--acceptance", action="append", required=True)
    arg_parser.add_argument("--stop-condition", action="append", required=True)
    arg_parser.add_argument("--dry-run", action="store_true")
    return arg_parser


def main() -> int:
    args = parser().parse_args()
    if not SLUG_RE.fullmatch(args.slug):
        raise PreparationError("--slug must contain lowercase letters, digits, and single hyphens only")
    if args.branch and (not BRANCH_RE.fullmatch(args.branch) or ".." in args.branch):
        raise PreparationError("--branch contains unsupported characters")

    workspace = Path(args.workspace_root).expanduser().resolve()
    if not workspace.is_dir():
        raise PreparationError(f"workspace root is not a directory: {workspace}")
    workspace_root_result = run_git(workspace, "rev-parse", "--show-toplevel")
    workspace_repo_root = Path(workspace_root_result.stdout.strip()).resolve()
    if workspace_repo_root != workspace:
        raise PreparationError(f"--workspace-root must be the root git repository: expected {workspace_repo_root}")
    ignore_result = run_git(
        workspace,
        "check-ignore",
        "--quiet",
        "--no-index",
        "tmp/subagents/.prepare-subagent-task",
        check=False,
    )
    if ignore_result.returncode != 0:
        raise PreparationError("workspace root must ignore tmp/ before preparing subagent work")

    repository = resolve_from(workspace, args.repository)
    require_under(repository, workspace, "repository")
    parent_task = resolve_from(workspace, args.parent_task)
    if not parent_task.is_dir() or not (parent_task / "README.md").is_file():
        raise PreparationError(f"parent task is missing README.md: {parent_task}")
    require_under(parent_task, workspace / "atlas-ai-docs" / "tasks", "parent task")

    repo_root_result = run_git(repository, "rev-parse", "--show-toplevel")
    repo_root = Path(repo_root_result.stdout.strip()).resolve()
    if repo_root != repository:
        raise PreparationError(f"--repository must be the git top level: expected {repo_root}")
    write_paths = normalize_write_paths(args.write_path, repository)

    baseline_result = run_git(repository, "rev-parse", "--verify", f"{args.baseline}^{{commit}}")
    baseline_commit = baseline_result.stdout.strip()

    if args.branch:
        branch_result = run_git(repository, "show-ref", "--verify", f"refs/heads/{args.branch}", check=False)
        if branch_result.returncode == 0:
            raise PreparationError(f"branch already exists: {args.branch}")

    suffix = args.suffix or datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", suffix):
        raise PreparationError("--suffix contains unsupported characters")
    repo_name = re.sub(r"[^A-Za-z0-9._-]+", "-", repository.name)
    runtime_dir = (workspace / "tmp" / "subagents" / f"{repo_name}-{args.slug}-{suffix}").resolve()
    require_under(runtime_dir, workspace / "tmp", "runtime directory")
    worktree = runtime_dir / "worktree"
    status_file = runtime_dir / "status.md"
    metadata_file = runtime_dir / "metadata.json"
    prompt_file = runtime_dir / "prompt.md"
    task_dir = parent_task / "subagents" / args.slug
    task_file = task_dir / "README.md"
    registry_file = parent_task / "subagents" / "README.md"

    collisions = [path for path in (runtime_dir, task_dir) if path.exists()]
    if collisions:
        raise PreparationError("refusing to reuse existing path(s): " + ", ".join(map(str, collisions)))
    registry_content = ""
    if registry_file.exists():
        registry_content = registry_file.read_text(encoding="utf-8")
        if f"/{args.slug}/README.md" in registry_content or f"-{args.slug}-" in registry_content:
            raise PreparationError(f"subtask already appears in registry: {args.slug}")

    branch_display = args.branch or f"detached at {baseline_commit[:12]}"
    task_content = f"""# Subagent: {args.title}

## Status

- State: planned
- Owner: main agent
- Agent: unassigned
- Repository: `{repository}`
- Baseline: `{baseline_commit}`
- Runtime: `{runtime_dir}`
- Worktree: `{worktree}`
- Branch: `{branch_display}`

## Requirements

{markdown_list(args.requirement)}

## Non-goals

{markdown_list(args.non_goal)}

## Allowed Write Set

{markdown_list(f'`{item}`' for item in write_paths)}

## Implementation Plan

{markdown_list(args.plan_step)}

## Test Plan

{markdown_list(args.test)}

## Acceptance Checklist

{markdown_list(f'[ ] {item}' for item in args.acceptance)}

## Stop Conditions

{markdown_list(args.stop_condition)}

## Checkpoints

| Checkpoint | State | Evidence |
|---|---|---|
| prepared | complete | Worktree prepared at `{worktree}` from `{baseline_commit}`. |
| inspected | pending | |
| implemented | pending | |
| tested | pending | |
| ready-for-review | pending | |

## Blockers And Decisions

None.

## Implementation Findings

None.

## Final Review

Pending main-agent review. The subagent must not commit or integrate changes.
"""

    status_content = f"""# Subagent Runtime Status

- State: planned
- Current checkpoint: prepared
- Agent: unassigned
- Baseline: {baseline_commit}
- Worktree: {worktree}
- Last update: {datetime.now(timezone.utc).isoformat()}

## Checkpoints

| Checkpoint | State | Evidence |
|---|---|---|
| prepared | complete | Detached or explicitly branched worktree created. |
| inspected | pending | |
| implemented | pending | |
| tested | pending | |
| ready-for-review | pending | |

## Blocker

- Blocking condition: none
- Evidence: none
- Decision needed: none
- Safe state of worktree: prepared

## Findings

None.
"""

    prompt_content = f"""Use the frozen task at `{task_file}`.

Work only in `{worktree}` at baseline `{baseline_commit}`.

Allowed write set:
{markdown_list(f'`{item}`' for item in write_paths)}

Rules:
- Inspect current code before editing.
- Do not edit the root task repository.
- Update `{status_file}` at every checkpoint.
- Do not commit, merge, rebase, cherry-pick, push, remove files, or clean the worktree.
- Stop on any documented stop condition or unresolved semantic decision.
- On a blocker, set state to `blocked`, record evidence and the exact decision needed, then stop.
- Finish in state `ready-for-review`; completion does not mean acceptance.
- Report changed files, exact tests, results, blockers, and residual risks.
"""

    metadata = {
        "title": args.title,
        "slug": args.slug,
        "state": "planned",
        "repository": str(repository),
        "baseline": baseline_commit,
        "runtime_dir": str(runtime_dir),
        "worktree": str(worktree),
        "branch": args.branch,
        "task_file": str(task_file),
        "status_file": str(status_file),
        "prompt_file": str(prompt_file),
        "allowed_write_set": write_paths,
    }

    worktree_command = ["git", "-C", str(repository), "worktree", "add"]
    if args.branch:
        worktree_command.extend(["-b", args.branch])
    else:
        worktree_command.append("--detach")
    worktree_command.extend([str(worktree), baseline_commit])

    summary = {
        **metadata,
        "dry_run": args.dry_run,
        "worktree_command": worktree_command,
    }
    if args.dry_run:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    runtime_dir.mkdir(parents=True, exist_ok=False)
    worktree_result = subprocess.run(worktree_command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if worktree_result.returncode != 0:
        status_file.write_text(
            status_content.replace("- State: planned", "- State: failed")
            + f"\n## Preparation Failure\n\n{worktree_result.stderr.strip()}\n",
            encoding="utf-8",
        )
        raise PreparationError(
            f"git worktree add failed; runtime evidence retained at {runtime_dir}: {worktree_result.stderr.strip()}"
        )

    task_dir.mkdir(parents=True, exist_ok=False)
    task_file.write_text(task_content, encoding="utf-8")
    status_file.write_text(status_content, encoding="utf-8")
    metadata_file.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    prompt_file.write_text(prompt_content, encoding="utf-8")

    registry_file.parent.mkdir(parents=True, exist_ok=True)
    registry_row = (
        f"| unassigned | `{runtime_dir}` | `{repository.name}` | "
        f"{', '.join(f'`{item}`' for item in write_paths)} | planned | none |\n"
    )
    if registry_file.exists():
        registry_file.write_text(registry_content.rstrip() + "\n" + registry_row, encoding="utf-8")
    else:
        registry_file.write_text(
            "# Subagent Tasks\n\n"
            "| Agent | Runtime | Repository | Allowed Write Set | State | Blocker |\n"
            "|---|---|---|---|---|---|\n"
            + registry_row,
            encoding="utf-8",
        )

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PreparationError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
