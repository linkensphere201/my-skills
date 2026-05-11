#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a tracked background task and write durable status files.")
    parser.add_argument("--command-json", required=True, help="JSON file produced by start_bg_task.py.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.command_json).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))

    command = config["command"]
    working_directory = Path(config["working_directory"]).resolve()
    stdout_log = Path(config["stdout_log"]).resolve()
    stderr_log = Path(config["stderr_log"]).resolve()
    child_pid_path = Path(config["child_pid_path"]).resolve()
    runtime_status_path = Path(config["runtime_status_path"]).resolve()
    exit_code_path = Path(config["exit_code_path"]).resolve()

    child_started_at: str | None = None
    process: subprocess.Popen[bytes] | None = None

    try:
        with stdout_log.open("ab") as stdout_file, stderr_log.open("ab") as stderr_file:
            process = subprocess.Popen(
                command,
                cwd=working_directory,
                stdout=stdout_file,
                stderr=stderr_file,
                start_new_session=True,
            )
            child_started_at = now_iso()
            child_pid_path.write_text(f"{process.pid}\n", encoding="utf-8")
            write_json(
                runtime_status_path,
                {
                    "runner_pid": None,
                    "child_pid": process.pid,
                    "child_started_at": child_started_at,
                    "status": "running",
                    "exit_code": None,
                },
            )
            exit_code = process.wait()

        exit_code_path.write_text(f"{exit_code}\n", encoding="utf-8")
        write_json(
            runtime_status_path,
            {
                "runner_pid": None,
                "child_pid": process.pid,
                "child_started_at": child_started_at,
                "child_finished_at": now_iso(),
                "status": "exited",
                "exit_code": exit_code,
            },
        )
        return int(exit_code)
    except Exception as exc:
        stderr_log.parent.mkdir(parents=True, exist_ok=True)
        with stderr_log.open("ab") as stderr_file:
            stderr_file.write((str(exc) + "\n").encode("utf-8"))
        exit_code_path.write_text("1\n", encoding="utf-8")
        write_json(
            runtime_status_path,
            {
                "runner_pid": None,
                "child_pid": process.pid if process else None,
                "child_started_at": child_started_at,
                "child_finished_at": now_iso(),
                "status": "failed",
                "exit_code": 1,
                "error": str(exc),
            },
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
