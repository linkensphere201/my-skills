#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import signal
import time
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_pid(path: Path) -> int | None:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    return int(text) if text.isdigit() else None


def process_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def stop_process(pid: int | None, label: str) -> dict[str, object]:
    if pid is None:
        return {"label": label, "pid": None, "action": "pid_not_recorded"}
    if not process_exists(pid):
        return {"label": label, "pid": pid, "action": "already_exited"}

    try:
        os.killpg(pid, signal.SIGTERM)
        target = "process_group"
    except ProcessLookupError:
        return {"label": label, "pid": pid, "action": "already_exited"}
    except Exception:
        os.kill(pid, signal.SIGTERM)
        target = "process"

    for _ in range(10):
        if not process_exists(pid):
            return {"label": label, "pid": pid, "action": "stopped", "target": target, "signal": "SIGTERM"}
        time.sleep(0.1)

    try:
        os.killpg(pid, signal.SIGKILL)
        target = "process_group"
    except Exception:
        os.kill(pid, signal.SIGKILL)
        target = "process"
    return {"label": label, "pid": pid, "action": "stopped", "target": target, "signal": "SIGKILL"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stop a tracked background task from metadata.json.")
    parser.add_argument("--metadata", required=True, help="Path to metadata.json produced by start_bg_task.py.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metadata_path = Path(args.metadata).expanduser().resolve()
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    task_directory = Path(metadata["task_directory"]).resolve()
    child_pid = read_pid(Path(metadata["child_pid"]).resolve()) if metadata.get("child_pid") else None
    runner_pid = int(metadata["pid"]) if metadata.get("pid") else None

    results = [
        stop_process(child_pid, "child"),
        stop_process(runner_pid, "runner"),
    ]

    stop_status_path = task_directory / "stop-status.json"
    payload = {
        "metadata": str(metadata_path),
        "stopped_at": now_iso(),
        "results": results,
    }
    stop_status_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(stop_status_path.read_text(encoding="utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
