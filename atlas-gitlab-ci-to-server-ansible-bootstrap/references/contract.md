# Workflow Contract

## Inputs

| Input | Default | Requirement |
|---|---|---|
| `--atlas-repo` | none | Existing absolute Git working-tree path |
| `--branch` | none | Exact remote branch to publish |
| `--commit` | none | Full 40-character commit SHA |
| `--remote` | `origin` | Git remote used for non-force push and GitLab project discovery |
| `--token-env` | `GITLAB_TOKEN` | Environment variable containing a GitLab API token |
| `--target` | none | SSH target such as `maodan@10.10.0.188` |
| `--ansible-dir` | none | Absolute remote atlas-ansible directory |
| `--publish-job` | `publish_docker_manual` | Manual GitLab CI image job |
| `--package-file` | `inventory/group_vars/all/package.yml` | Remote package definition |
| `--poll-seconds` | `10` | CI polling interval |
| `--timeout-seconds` | `7200` | Pipeline/job discovery and completion timeout |
| `--confirmed-package-replace` | disabled | Required after confirming replacement of the old image archive |
| `--confirmed-disruptive-deploy` | disabled | Required after confirming Atlas service interruption |

## CI State Rules

- `manual`: play the exact job once.
- `created`, `pending`, `preparing`, `running`, `waiting_for_resource`: wait.
- `success`: continue.
- `failed`, `canceled`, `skipped`: stop and report IDs and status.
- missing pipeline/job: poll until timeout, then stop.

Never select a pipeline by branch alone. Match both exact branch and full SHA.
Never pick an older successful job from another pipeline.

## Remote Package Update

Modify only the YAML list item whose active key is `docker_image_atlas`:

- `value` becomes the target branch;
- `extra.job` becomes the selected publish job;
- `extra.commit_sha` becomes the full target SHA.

Preserve comments and every other image entry. Fail if the block is absent,
duplicated, malformed, or cannot be updated exactly once.

After `00.package.yml`, require the generated `inventory/group_vars/all/image.yml`
Atlas image line to contain the target short SHA. Pipeline IID verification is
recommended when the image naming convention contains it.

## Failure Boundaries

| Failure | Required action |
|---|---|
| Push rejected | Stop; do not force-push |
| Pipeline absent | Report branch/SHA and timeout |
| CI job failed | Report pipeline/job IDs; inspect trace before any retry |
| Package update rejected | Leave services running and stop |
| `00.package.yml` failed | Leave services running and stop; inspect whether the old archive was already replaced |
| `01.push_image.yml` failed | Leave services running and stop |
| `03.undeploy_atlas.yml` failed | Stop and inspect actual container state |
| `02.deploy_atlas.yml` failed | Cluster may be unavailable; report immediately |
| Version/image mismatch | Do not benchmark; treat deployment as failed verification |

## Outputs

Always return a compact deployment record containing:

- repository remote and branch;
- full commit SHA;
- GitLab pipeline ID/IID and publish job ID;
- published image tag when available;
- each playbook exit status and recap;
- per-node Atlas container image, version, state, and restart count;
- endpoint checks and remaining smoke tests.
