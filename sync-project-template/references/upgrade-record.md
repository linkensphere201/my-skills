# Upgrade Evidence And Partial Adoption

Read this when reviewing previous upgrades or recording an approved adoption.

## Initial Source

`.template-source.json` belongs to project creation. Current generator v1 writes
version, commit and dirty fields, but not rendering variables or per-file hashes.
Do not pretend these missing facts exist, and do not rewrite this file after
adopting only one component.

A version-only or dirty source is not a trustworthy clean baseline. The user
may identify an archived original rendered file or a separately verified
baseline; record that evidence before relying on it.

## Per-Project Ledger

Use `.template-sync.json` for upgrade receipts when the project has no established
equivalent record. Preserve existing entries and schema. Do not overwrite an
unknown or malformed ledger; ask how to reconcile it.

A receipt can use this shape:

```json
{
  "schema_version": 1,
  "history": [
    {
      "target_commit": "<full immutable commit>",
      "target_version": "<label, informational only>",
      "template_repository": "<verified source identity>",
      "components": [
        {
          "source_path": "AGENTS.md",
          "destination_path": "AGENTS.md",
          "scope": "full-component",
          "base_commit": "<verified component baseline commit>",
          "before_sha256": "<exact pre-edit bytes>",
          "after_sha256": "<exact validated bytes>",
          "status": "applied",
          "validation": ["<checks actually performed>"]
        }
      ]
    }
  ]
}
```

Record the actual approval/date in a form consistent with the project's existing
audit conventions. Never store credentials, private remote tokens or unrelated
project contents in the ledger.

## Baseline Rules

- A validated full-component receipt can advance that component's baseline to
  its recorded target commit. Local customization may remain; the next three-way
  review still compares current project content with the target template.
- For section-only or selective-hunk adoption, set scope=partial and record the
  approved patch/section description plus the retained base_commit. Do not claim
  the full component has advanced. Store reviewed patch evidence in the project's
  established migration-log location if needed.
- Partial receipts must be replayed/reviewed on the next run. If an accepted
  section has no stable boundaries or evidence is missing, use manual review
  instead of silently replacing or repeatedly reapplying it.
- Exact hashes detect drift; a matching hash alone does not prove a semantic
  merge or test was correct.
- Mark changes validated only after relevant checks pass. A pending/failed
  attempt must not advance a component baseline.
- Protected documents and rejected changes remain unadopted. Reviewing a target
  version is not equivalent to upgrading the project to that version.

## Acceptance Cases

Before considering a synchronization complete, check the applicable cases:

1. Same template revision: no content or metadata write.
2. Unchanged local AGENTS, changed template AGENTS: proposed patch, no write
   before approval.
3. Both sides edited a rule: conflict and explanation, not full-file replacement.
4. New component collides with an existing file: no overwrite.
5. Upstream removes a component: report removal, preserve local file.
6. Missing baseline or unrecoverable rendering variables: advisory-only.
7. Only one section approved: partial receipt, original source unchanged.
8. File changes after preview: refresh approval instead of applying stale hunks.
9. Validation fails: no successful upgrade claim or baseline advance.
