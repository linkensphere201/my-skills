#!/usr/bin/env python3
"""Publish an Atlas commit through GitLab CI and deploy it with atlas-ansible."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
from urllib.parse import quote, urlparse


TERMINAL_JOB_FAILURES = {"failed", "canceled", "skipped"}
WAITING_JOB_STATES = {
    "created",
    "pending",
    "preparing",
    "running",
    "waiting_for_resource",
    "scheduled",
}

PACKAGE_UPDATER = r'''
import pathlib
import re
import sys

path = pathlib.Path(sys.argv[1])
branch, commit, job = sys.argv[2:5]
text = path.read_text()
starts = list(re.finditer(r"(?m)^(?P<i>[ ]*)-[ ]+key:[ ]*docker_image_atlas[ ]*$", text))
if len(starts) != 1:
    raise SystemExit("expected exactly one active docker_image_atlas block, got {}".format(len(starts)))
start_match = starts[0]
indent = start_match.group("i")
next_item = re.search(r"(?m)^{}-[ ]+key:[ ]*".format(re.escape(indent)), text[start_match.end():])
metas = re.search(r"(?m)^metas:[ ]*", text[start_match.end():])
ends = [m.start() for m in (next_item, metas) if m]
end = start_match.end() + (min(ends) if ends else len(text) - start_match.end())
block = text[start_match.start():end]

def replace_active(name, value, source):
    pattern = r"(?m)^(?P<i>[ ]*){}:[ ]*[^#\n]*$".format(re.escape(name))
    matches = list(re.finditer(pattern, source))
    if len(matches) != 1:
        raise SystemExit("expected one active {} in docker_image_atlas block, got {}".format(name, len(matches)))
    return re.sub(pattern, lambda m: "{}{}: {}".format(m.group("i"), name, value), source, count=1)

block = replace_active("value", branch, block)
block = replace_active("job", job, block)
active_commit = list(re.finditer(r"(?m)^(?P<i>[ ]*)commit_sha:[ ]*[^#\n]*$", block))
if len(active_commit) == 1:
    block = re.sub(
        r"(?m)^(?P<i>[ ]*)commit_sha:[ ]*[^#\n]*$",
        lambda m: "{}commit_sha: {}".format(m.group("i"), commit),
        block,
        count=1,
    )
elif len(active_commit) == 0:
    job_match = re.search(r"(?m)^(?P<i>[ ]*)job:[ ]*[^#\n]*$", block)
    if not job_match:
        raise SystemExit("active job field disappeared while adding commit_sha")
    insertion = "\n{}commit_sha: {}".format(job_match.group("i"), commit)
    block = block[:job_match.end()] + insertion + block[job_match.end():]
else:
    raise SystemExit("multiple active commit_sha fields in docker_image_atlas block")

updated = text[:start_match.start()] + block + text[end:]
if updated == text:
    print("package config already matches target")
else:
    path.write_text(updated)
    print("updated {} for branch {} commit {} job {}".format(path, branch, commit, job))
'''


class WorkflowError(RuntimeError):
    pass


def display_command(command: list[str], secret_input: bool = False) -> None:
    prefix = "<token via stdin> | " if secret_input else ""
    print("+ {}{}".format(prefix, shlex.join(command)), flush=True)


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    capture: bool = False,
    dry_run: bool = False,
    secret_input: bool = False,
) -> subprocess.CompletedProcess[str]:
    display_command(command, secret_input=secret_input)
    if dry_run:
        return subprocess.CompletedProcess(command, 0, "", "")
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        input=input_text,
        text=True,
        capture_output=capture,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() if capture else ""
        raise WorkflowError(
            "command failed with exit code {}{}".format(
                result.returncode, ": " + detail if detail else ""
            )
        )
    return result


def git_output(repo: Path, *args: str, dry_run: bool = False) -> str:
    result = run(["git", *args], cwd=repo, capture=True, dry_run=dry_run)
    return result.stdout.strip()


def infer_gitlab_host(remote_url: str) -> str:
    if "://" in remote_url:
        host = urlparse(remote_url).hostname
    else:
        match = re.match(r"(?:[^@]+@)?([^:]+):", remote_url)
        host = match.group(1) if match else None
    if not host:
        raise WorkflowError("cannot infer GitLab host from remote URL: {}".format(remote_url))
    return host


def glab_json(
    repo: Path,
    host: str,
    token: str,
    endpoint: str,
    *,
    method: str = "GET",
) -> object:
    env = os.environ.copy()
    env["GLAB_TOKEN"] = token
    env["GITLAB_TOKEN"] = token
    command = ["glab", "api", "--hostname", host, "--method", method, endpoint]
    result = run(command, cwd=repo, env=env, capture=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise WorkflowError("glab returned invalid JSON") from error


def wait_for_pipeline(
    repo: Path,
    host: str,
    token: str,
    branch: str,
    commit: str,
    deadline: float,
    poll_seconds: int,
) -> dict[str, object]:
    endpoint = "projects/:id/pipelines?ref={}&sha={}&per_page=20".format(
        quote(branch, safe=""), commit
    )
    while time.monotonic() < deadline:
        pipelines = glab_json(repo, host, token, endpoint)
        if isinstance(pipelines, list):
            matches = [
                item
                for item in pipelines
                if item.get("sha") == commit and item.get("ref") == branch
            ]
            if matches:
                return max(matches, key=lambda item: int(item["id"]))
        time.sleep(poll_seconds)
    raise WorkflowError("timed out waiting for pipeline for exact branch and SHA")


def wait_for_job(
    repo: Path,
    host: str,
    token: str,
    pipeline_id: int,
    job_name: str,
    deadline: float,
    poll_seconds: int,
) -> dict[str, object]:
    endpoint = "projects/:id/pipelines/{}/jobs?include_retried=true&per_page=100".format(
        pipeline_id
    )
    played = False
    while time.monotonic() < deadline:
        jobs = glab_json(repo, host, token, endpoint)
        matches = [job for job in jobs if job.get("name") == job_name]
        if not matches:
            time.sleep(poll_seconds)
            continue
        job = max(matches, key=lambda item: int(item["id"]))
        job_id = int(job["id"])
        status = str(job["status"])
        print("CI job id={} status={}".format(job_id, status), flush=True)
        if status == "success":
            return job
        if status == "manual" and not played:
            glab_json(repo, host, token, "projects/:id/jobs/{}/play".format(job_id), method="POST")
            played = True
        elif status in TERMINAL_JOB_FAILURES:
            raise WorkflowError(
                "CI job {} ended with status {}; inspect {} before retrying".format(
                    job_id, status, job.get("web_url", "the GitLab job trace")
                )
            )
        elif status not in WAITING_JOB_STATES and status != "manual":
            raise WorkflowError("unsupported CI job state {} for job {}".format(status, job_id))
        time.sleep(poll_seconds)
    raise WorkflowError("timed out waiting for CI job {}".format(job_name))


def ssh(target: str, remote_command: str) -> list[str]:
    return [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=10",
        target,
        remote_command,
    ]


def validate_local(args: argparse.Namespace) -> tuple[Path, str, str, str]:
    repo = Path(args.atlas_repo).expanduser().resolve()
    if not repo.is_dir():
        raise WorkflowError("Atlas repository does not exist: {}".format(repo))
    if not re.fullmatch(r"[0-9a-fA-F]{40}", args.commit):
        raise WorkflowError("--commit must be a full 40-character SHA")
    commit = git_output(repo, "rev-parse", "{}^{{commit}}".format(args.commit)).lower()
    if commit != args.commit.lower():
        raise WorkflowError("resolved commit differs from requested SHA")
    branch_commit = git_output(repo, "rev-parse", "refs/heads/{}^{{commit}}".format(args.branch)).lower()
    if branch_commit != commit:
        raise WorkflowError("target branch tip does not equal requested commit")
    remote_url = git_output(repo, "remote", "get-url", args.remote)
    return repo, commit, remote_url, infer_gitlab_host(remote_url)


def remote_preflight(args: argparse.Namespace, dry_run: bool) -> None:
    command = (
        "set -eu; test -d {d}; test -f {d}/{p}; command -v ansible-playbook >/dev/null; "
        "sudo -n true"
    ).format(d=shlex.quote(args.ansible_dir), p=shlex.quote(args.package_file))
    run(ssh(args.target, command), dry_run=dry_run)


def update_remote_package(args: argparse.Namespace, commit: str, dry_run: bool) -> None:
    package_path = str(Path(args.ansible_dir) / args.package_file)
    if dry_run:
        display_command(
            ssh(
                args.target,
                "sudo python3 <embedded-package-updater> {} {} {} {}".format(
                    shlex.quote(package_path),
                    shlex.quote(args.branch),
                    shlex.quote(commit),
                    shlex.quote(args.publish_job),
                ),
            )
        )
        return
    encoded = base64.b64encode(PACKAGE_UPDATER.encode()).decode()
    loader = "import base64;exec(base64.b64decode({!r}))".format(encoded)
    remote = shlex.join(
        [
            "sudo",
            "python3",
            "-c",
            loader,
            package_path,
            args.branch,
            commit,
            args.publish_job,
        ]
    )
    run(ssh(args.target, remote), dry_run=dry_run)


def run_playbook(
    args: argparse.Namespace,
    playbook: str,
    *,
    token: str | None = None,
    host: str | None = None,
    dry_run: bool = False,
) -> None:
    prefix = "cd {} && ".format(shlex.quote(args.ansible_dir))
    if token is None:
        remote = prefix + "sudo ansible-playbook " + shlex.quote(playbook)
        run(ssh(args.target, remote), dry_run=dry_run)
        return
    remote = (
        prefix
        + "IFS= read -r GITLAB_TOKEN; export GITLAB_TOKEN; "
        + "export GITLAB_HOST={}; sudo -E ansible-playbook {}".format(
            shlex.quote("https://" + str(host)), shlex.quote(playbook)
        )
    )
    run(
        ssh(args.target, remote),
        input_text=token + "\n" if not dry_run else None,
        dry_run=dry_run,
        secret_input=True,
    )


def verify_prepared_image(args: argparse.Namespace, commit: str, dry_run: bool) -> None:
    image_file = str(Path(args.ansible_dir) / "inventory/group_vars/all/image.yml")
    short = commit[:8]
    remote = (
        "set -eu; line=$(grep 'docker_image_atlas:' {}); "
        "printf '%s\\n' \"$line\"; printf '%s' \"$line\" | grep -F {} >/dev/null"
    ).format(shlex.quote(image_file), shlex.quote(short))
    run(ssh(args.target, remote), dry_run=dry_run)


def show_cluster_state(args: argparse.Namespace, dry_run: bool) -> None:
    remote = (
        "cd {} && sudo ansible all -m shell -a {}"
    ).format(
        shlex.quote(args.ansible_dir),
        shlex.quote("docker ps --no-trunc | grep atlas || true"),
    )
    run(ssh(args.target, remote), dry_run=dry_run)


def prepare(args: argparse.Namespace, repo: Path, commit: str, host: str) -> None:
    if args.dry_run:
        run(
            ["git", "push", args.remote, "{}:refs/heads/{}".format(commit, args.branch)],
            cwd=repo,
            dry_run=True,
        )
        print("+ glab: find exact branch/SHA pipeline, play job, poll to success")
        update_remote_package(args, commit, True)
        run_playbook(args, "playbooks/00.package.yml", token="<token>", host=host, dry_run=True)
        verify_prepared_image(args, commit, True)
        return

    if not args.confirmed_package_replace:
        raise WorkflowError(
            "prepare phase requires --confirmed-package-replace after explicit user confirmation"
        )
    token = os.environ.get(args.token_env)
    if not token:
        raise WorkflowError("environment variable {} is empty".format(args.token_env))
    run(
        ["git", "push", args.remote, "{}:refs/heads/{}".format(commit, args.branch)],
        cwd=repo,
    )
    deadline = time.monotonic() + args.timeout_seconds
    pipeline = wait_for_pipeline(
        repo, host, token, args.branch, commit, deadline, args.poll_seconds
    )
    print(
        "GitLab pipeline id={} iid={} sha={}".format(
            pipeline.get("id"), pipeline.get("iid"), pipeline.get("sha")
        ),
        flush=True,
    )
    job = wait_for_job(
        repo,
        host,
        token,
        int(pipeline["id"]),
        args.publish_job,
        deadline,
        args.poll_seconds,
    )
    print(
        "GitLab publish job id={} succeeded url={}".format(
            job["id"], job.get("web_url", "unknown")
        ),
        flush=True,
    )
    update_remote_package(args, commit, False)
    run_playbook(args, "playbooks/00.package.yml", token=token, host=host)
    verify_prepared_image(args, commit, False)


def deploy(args: argparse.Namespace, commit: str) -> None:
    if not args.dry_run and not args.confirmed_disruptive_deploy:
        raise WorkflowError(
            "deploy phase requires --confirmed-disruptive-deploy after explicit user confirmation"
        )
    verify_prepared_image(args, commit, args.dry_run)
    run_playbook(args, "playbooks/01.push_image.yml", dry_run=args.dry_run)
    run_playbook(args, "playbooks/03.undeploy_atlas.yml", dry_run=args.dry_run)
    run_playbook(args, "playbooks/02.deploy_atlas.yml", dry_run=args.dry_run)
    show_cluster_state(args, args.dry_run)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("prepare", "deploy", "all"), required=True)
    parser.add_argument("--atlas-repo", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--token-env", default="GITLAB_TOKEN")
    parser.add_argument("--target", required=True)
    parser.add_argument("--ansible-dir", required=True)
    parser.add_argument("--publish-job", default="publish_docker_manual")
    parser.add_argument(
        "--package-file", default="inventory/group_vars/all/package.yml"
    )
    parser.add_argument("--poll-seconds", type=int, default=10)
    parser.add_argument("--timeout-seconds", type=int, default=7200)
    parser.add_argument("--confirmed-package-replace", action="store_true")
    parser.add_argument("--confirmed-disruptive-deploy", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        repo, commit, _remote_url, host = validate_local(args)
        remote_preflight(args, args.dry_run)
        if args.phase in {"prepare", "all"}:
            prepare(args, repo, commit, host)
        if args.phase in {"deploy", "all"}:
            deploy(args, commit)
    except WorkflowError as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
