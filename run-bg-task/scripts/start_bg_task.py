#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "-", value).strip("-") or "task"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start a long-running command in the background with logs and PID metadata."
    )
    parser.add_argument("--name", required=True, help="Logical task name used in the run directory.")
    parser.add_argument("--working-directory", required=True, help="Directory where the command should run.")
    parser.add_argument(
        "--run-directory",
        default=".tmp/bg-tasks",
        help="Directory for task metadata. Relative paths are resolved from the working directory.",
    )
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    command = args.command
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise SystemExit("error: command is required after --")

    working_directory = Path(args.working_directory).expanduser().resolve()
    if not working_directory.is_dir():
        raise SystemExit(f"error: working directory does not exist: {working_directory}")

    run_root = Path(args.run_directory).expanduser()
    if not run_root.is_absolute():
        run_root = working_directory / run_root
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    task_directory = run_root / f"{timestamp}-{safe_name(args.name)}"
    task_directory.mkdir(parents=True, exist_ok=False)

    stdout_log = task_directory / "stdout.log"
    stderr_log = task_directory / "stderr.log"
    metadata_path = task_directory / "metadata.json"
    command_config_path = task_directory / "command.json"
    exit_code_path = task_directory / "exit-code.txt"
    child_pid_path = task_directory / "child-pid.txt"
    runtime_status_path = task_directory / "runtime-status.json"

    for log_path in (stdout_log, stderr_log):
        log_path.touch()

    runner_script = Path(__file__).resolve().with_name("bg_task_runner.py")
    command_config = {
        "command": command,
        "working_directory": str(working_directory),
        "stdout_log": str(stdout_log),
        "stderr_log": str(stderr_log),
        "exit_code_path": str(exit_code_path),
        "child_pid_path": str(child_pid_path),
        "runtime_status_path": str(runtime_status_path),
    }
    write_json(command_config_path, command_config)

    runner_command = [sys.executable, str(runner_script), "--command-json", str(command_config_path)]
    with open(os.devnull, "rb") as devnull:
        process = subprocess.Popen(
            runner_command,
            cwd=working_directory,
            stdin=devnull,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

    metadata = {
        "name": args.name,
        "pid": process.pid,
        "pid_type": "runner",
        "command": command,
        "working_directory": str(working_directory),
        "task_directory": str(task_directory),
        "stdout_log": str(stdout_log),
        "stderr_log": str(stderr_log),
        "command_config": str(command_config_path),
        "runner_script": str(runner_script),
        "exit_code": str(exit_code_path),
        "child_pid": str(child_pid_path),
        "runtime_status": str(runtime_status_path),
        "started_at": now_iso(),
    }
    write_json(metadata_path, metadata)

    print(
        json.dumps(
            {
                "pid": process.pid,
                "task_directory": str(task_directory),
                "stdout_log": str(stdout_log),
                "stderr_log": str(stderr_log),
                "metadata": str(metadata_path),
                "exit_code": str(exit_code_path),
                "child_pid": str(child_pid_path),
                "runtime_status": str(runtime_status_path),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
