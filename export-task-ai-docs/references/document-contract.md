# Project AI Documentation Contract

Use this contract to produce a consistent, evidence-based feature record. Adapt filenames to a strong existing project convention, but preserve every mandatory topic and its separate review conclusion.

## Default File Set

| File | Required | Purpose |
|---|---:|---|
| `README.md` | Yes | Scope, provenance, reading order, support summary, and current status |
| `01-requirements.md` | Yes | Product requirements, boundaries, and acceptance criteria |
| `02-requirements-review.md` | Yes | Requirement completeness and scope review conclusions |
| `03-design.md` | Yes | Accepted architecture, contracts, and runtime semantics |
| `04-design-review.md` | Yes | Design alternatives, findings, decisions, and residual risks |
| `05-implementation.md` | Yes | Code-level implementation map and actual behavior |
| `06-implementation-review.md` | Yes | Code review findings, dispositions, and remaining technical risk |
| `07-testing.md` | Yes | Coverage map, commands, environments, and observed results |
| `08-testing-review.md` | Yes | Test adequacy, gaps, reliability, and release confidence |
| `09-usage.md` | Conditional | Supported syntax or APIs, examples, permissions, and limitations |
| `10-release-operations.md` | Conditional | Upgrade, rollback, compatibility, deployment, and observability |

If the project already combines optional topics, keep its convention and explain the mapping in `README.md`. Do not combine a stage document with its review document: the separation makes accepted behavior distinguishable from review history and residual risk.

## Evidence Labels

Use explicit labels or wording that distinguishes these states:

- **Confirmed requirement**: explicitly accepted by the user or stable task decision.
- **Implemented**: verified in current source on the documented revision.
- **Covered by test**: a test exists and its assertion was inspected.
- **Executed**: a recorded command has a known result for a named revision and environment.
- **Historical evidence**: valid only for an older revision or environment.
- **Deferred**: intentionally excluded from the current scope.
- **Unverified**: plausible but not demonstrated by inspected evidence.
- **Open issue**: a known mismatch, defect, or unresolved decision.

Do not convert "covered by test" into "passed" without an execution result. Do not describe a proposed design as implemented.

## README.md

Include:

1. document purpose and intended AI audience;
2. feature, branch, base branch, and commit scope;
3. source repositories and test repositories;
4. reading order with relative links;
5. concise supported and unsupported behavior;
6. core invariants;
7. implementation and verification status;
8. known open items or a clear statement that none were found.

Keep this file navigational. Put detailed rationale and evidence in the stage documents.

## Requirements

Include:

- problem statement and user value;
- actors and entry points;
- goals and non-goals;
- functional requirements;
- permissions and security requirements;
- consistency, transaction, and failure requirements;
- persistence and compatibility requirements;
- performance or caching requirements;
- supported and unsupported matrix;
- measurable acceptance criteria.

State requirements independently of the chosen implementation where possible.

## Requirements Review

Review:

- whether scope is internally consistent;
- whether actors, permissions, lifecycle, and failure behavior are defined;
- whether compatibility and operational requirements are explicit;
- whether acceptance criteria can be tested;
- ambiguities that were resolved and the source of each decision;
- deferred requirements and why they are deferred.

End with one conclusion: `Approved`, `Approved with follow-ups`, or `Blocked`. Include the documented revision or decision date and list any follow-ups.

## Design

Include applicable topics:

- architecture and ownership boundaries;
- data model and persistence layout;
- public syntax, API, RPC, and metadata contracts;
- cache population, invalidation, and fallback behavior;
- authorization flow and trust boundaries;
- parsing, planning, execution, and result flow;
- transaction, cancellation, cleanup, and error semantics;
- concurrency and atomicity invariants;
- upgrade and downgrade compatibility;
- performance-sensitive paths;
- rejected responsibilities and explicit non-goals.

Use sequence or component diagrams only when they expose information that prose does not.

## Design Review

Capture decisions rather than a conversation transcript. For each material issue, record:

- issue or design question;
- alternatives considered;
- accepted decision;
- rationale and tradeoff;
- invariant established;
- residual risk or follow-up;
- implementation evidence when already available.

Review security, permissions, metadata consistency, failure atomicity, lifecycle cleanup, transaction boundaries, cache coherence, backward compatibility, and performance where relevant. End with an approval conclusion.

## Implementation

Describe the code that exists, not the implementation plan. Include:

- repository, branch, base, and commit provenance;
- module-by-module change map with repository-relative paths;
- data structures and ownership;
- persistence keys or schema changes;
- API, RPC, parser, planner, executor, and client-cache changes;
- authorization checks and error mapping;
- startup, update, cleanup, cancellation, and recovery paths;
- compatibility behavior for pre-feature data;
- intentional differences between product branches;
- known implementation limits.

For generated files, cite the source definition rather than treating generated output as the design source.

## Implementation Review

Lead with findings ordered by severity. Use a table containing at least:

| Severity | Area | Finding | Disposition | Evidence |
|---|---|---|---|---|

Include resolved findings when they explain important final invariants. Distinguish fixed, accepted, deferred, and still-open findings. Review at least:

- correctness and failure behavior;
- authorization and information exposure;
- lifecycle and cleanup;
- transaction ownership;
- concurrency and lock behavior;
- cache and remote-call behavior;
- persistence compatibility;
- cancellation and resource fanout;
- error classification;
- maintainability and bypassable internal entry points.

End with residual risk and an approval conclusion tied to a revision.

## Testing

Include a requirement-to-test coverage matrix. For each test layer, record:

- repository and test location;
- exact test or suite name;
- behavior asserted;
- command used;
- execution date and revision when available;
- environment prerequisites;
- result: passed, failed, not run, or historical;
- failure diagnosis when a failure was environmental or unrelated.

Separate unit, integration, E2E, restart/persistence, upgrade/rollback, authorization, negative-path, cancellation, concurrency, and performance evidence as applicable. Never hide skipped, ignored, flaky, or non-required cases.

## Testing Review

Assess:

- acceptance-criteria coverage;
- positive and negative path balance;
- permission coverage;
- persistence and restart coverage;
- upgrade and rollback coverage;
- concurrency, cancellation, and cleanup coverage;
- environment fidelity;
- flaky or timing-sensitive behavior;
- gaps that block release versus accepted residual gaps.

End with one conclusion: `Release evidence sufficient`, `Sufficient with follow-ups`, or `Insufficient`. Tie the conclusion to the tested revision.

## Usage

Create this document for user-visible syntax, APIs, commands, or administrative workflows. Include:

- prerequisites and permissions;
- setup and lifecycle sequence;
- minimal examples first, then advanced examples;
- expected result shape or behavior;
- supported and unsupported forms;
- common errors and recovery;
- transaction and consistency cautions;
- operational notes that affect users.

Use examples verified against the parser, API definitions, or tests. Do not document planned syntax as available.

## Release Operations

Create this document when persistence, wire contracts, deployment, or version compatibility matters. Include:

- pre-upgrade checks;
- forward-upgrade behavior with old data;
- first-write or migration behavior;
- mixed-version constraints;
- rollback safety and irreversible changes;
- backup and recovery considerations;
- observability and diagnostic signals;
- post-upgrade verification;
- known operational limitations.

If upgrade or rollback was not executed, state that explicitly and separate code-level compatibility reasoning from test evidence.

## Writing Rules

- Write concise technical English for future AI agents and engineers.
- Use stable terms consistently and add a glossary when terminology is overloaded.
- Prefer tables for support matrices, findings, and test coverage.
- Prefer repository-relative paths and symbol names over line numbers that quickly become stale.
- Use exact syntax and error names in code formatting.
- Keep requirements, design intent, implementation fact, and test evidence separate.
- Summarize decision history; do not reproduce chat chronology.
- Avoid promotional language and unsupported quality claims.
- Avoid absolute local paths, credentials, tokens, hostnames, and environment secrets.

## Final Quality Gate

Before completion, verify:

- the output matches the current target branch rather than another feature line;
- branch-specific differences are explicit;
- all mandatory files exist or are mapped to an established equivalent;
- review conclusions exist for all four stages;
- support matrices agree across all files;
- permissions and security behavior agree across requirements, design, implementation, and tests;
- test claims distinguish existence from execution;
- deferred and unsupported behavior is consistent;
- links resolve and filenames follow project conventions;
- no unrelated repository files changed.
