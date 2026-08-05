---
name: atlas-gitlab-ci-to-server-ansible-bootstrap
description: Publish an exact Atlas Git commit through a manual GitLab CI Docker job, wait for the image, update a remote atlas-ansible package definition, package and distribute the image, redeploy Atlas, and verify the result. Use when the user asks to push or publish an Atlas branch/commit and upgrade an Atlas server or cluster through GitLab CI plus atlas-ansible.
---

# Atlas GitLab CI To Ansible Deploy

Use `scripts/atlas_ci_ansible_deploy.py` as the deterministic orchestrator. Keep
CI preparation and service replacement as separate phases so the disruptive
phase has an explicit confirmation boundary.

## Required Inputs

Collect and echo these non-secret values before execution:

- absolute Atlas repository path;
- target branch and full 40-character commit SHA;
- Git remote, normally `origin`;
- GitLab token environment variable name, normally `GITLAB_TOKEN`;
- SSH target in `user@host` form;
- absolute remote `atlas-ansible` directory;
- CI job name, normally `publish_docker_manual`.

Never read a token from `.gitlab-ci.yml`, command history, or repository files.
Never print, persist, or pass the token as a command-line argument. The script
reads it from the selected environment variable and sends it over SSH stdin only
for `00.package.yml`.

Read [references/contract.md](references/contract.md) when changing defaults,
handling a failed CI job, or diagnosing package/deployment failures.

## Workflow

### 1. Preflight And Dry Run

Confirm that `glab`, `git`, `ssh`, and Python 3 exist. Confirm that the commit is
the exact target and belongs to the requested local branch. Run:

```bash
python3 <skill-dir>/scripts/atlas_ci_ansible_deploy.py \
  --phase all \
  --atlas-repo <absolute-atlas-repo> \
  --branch <branch> \
  --commit <full-sha> \
  --token-env GITLAB_TOKEN \
  --target <user@host> \
  --ansible-dir <absolute-remote-atlas-ansible-dir> \
  --dry-run
```

Review every resolved command and parameter. A dry run must not access the
token, push, trigger CI, edit the server, or run Ansible.

### 2. Confirm Package Replacement

Before `--phase prepare`, inspect the target `pull-images.py` and resolve
`image_dir`. If packaging can remove an existing archive, display the exact
resolved command, typically:

```text
sudo rm -rf <ansible-dir>/playbooks/roles/install/images/docker_images.tar.gz
```

Explain that this replaces the previous offline image archive and can consume
substantial network, disk, and CPU resources. Ask the user to reply exactly
`CONFIRMED`. This confirmation does not authorize service undeployment.

### 3. Prepare The Release

Run `--phase prepare` without the disruptive confirmation flag. This phase:

1. resolves and validates the full commit;
2. pushes it to the requested remote branch without force;
3. finds the pipeline for the exact branch and SHA;
4. plays `publish_docker_manual` when it is manual;
5. prints the pipeline ID and job ID and waits for success;
6. updates only the `docker_image_atlas` block in remote `package.yml`;
7. runs `00.package.yml` with the token supplied through stdin;
8. verifies generated `image.yml` contains the target short SHA.

Example:

```bash
python3 <skill-dir>/scripts/atlas_ci_ansible_deploy.py \
  --phase prepare \
  --atlas-repo <absolute-atlas-repo> \
  --branch <branch> \
  --commit <full-sha> \
  --token-env GITLAB_TOKEN \
  --target <user@host> \
  --ansible-dir <absolute-remote-atlas-ansible-dir> \
  --confirmed-package-replace
```

Stop on a failed CI job. Report its pipeline/job IDs and trace URL. Do not retry
or trigger another pipeline automatically.

### 4. Confirm The Disruptive Phase

Before `--phase deploy`, display the exact script command and these internal
commands with resolved target and directory:

```text
sudo ansible-playbook playbooks/01.push_image.yml
sudo ansible-playbook playbooks/03.undeploy_atlas.yml
sudo ansible-playbook playbooks/02.deploy_atlas.yml
```

Explain that `03.undeploy_atlas.yml` stops the current Atlas services, causes an
availability interruption, and that a failed deploy can leave the cluster down.
Ask the user to reply exactly `CONFIRMED`. Do not infer confirmation from a prior
unrelated deployment.

### 5. Deploy And Verify

After confirmation, run `--phase deploy --confirmed-disruptive-deploy` with the
same inputs. The script verifies the prepared package first, then distributes the
image, undeploys, deploys, and prints a cluster-wide Docker status snapshot.

Do not proceed to the next playbook unless the previous one exits successfully.
Afterward, independently verify:

- expected Graph, Store, and Meta containers are running;
- image tags contain the expected short SHA;
- `atlasd --version` reports the full target SHA;
- restart counts remain zero through a short stability window;
- Graph, Store, and Meta ports are reachable;
- recent logs contain no startup `panic`, `fatal`, or recurring `error`.

Report branch, full SHA, pipeline ID, job ID, image tag, Ansible recap, container
versions, and any unverified application-level checks. Do not claim plugin or
query health unless an actual plugin/Cypher smoke test ran.

## Safety And Recovery

- Never force-push. A non-fast-forward push must stop for user resolution.
- Never silently deploy a different pipeline or SHA.
- Never continue after an Ansible `failed` or `unreachable` result.
- Never run rollback automatically. Show the exact rollback image/config and
  commands, explain impact, and obtain a fresh `CONFIRMED`.
- Treat `undeploy`, rollback, service restart, and any playbook that removes or
  replaces running containers as dangerous under workspace rules.
- Leave `atlas/Cargo.lock` and generated RPC code out of commits.
