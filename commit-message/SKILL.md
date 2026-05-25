---
name: commit-message
description: Use when preparing, amending, squashing, or reviewing git commit messages in this Atlas workspace, especially when preserving source branch and original commit provenance.
---

# Commit Message

## Purpose

Keep Atlas commit history readable and provenance-preserving when Codex creates,
amends, squashes, or reviews commits.

## Format

Use this structure:

```text
commit title

body paragraph line 1
body paragraph line 2

Footer-Key: value
Footer-Key: value
```

Rules:

- Keep the title as the original commit title when the user asks to preserve it.
- Body text may wrap across multiple lines; do not leave overlong single-line bodies.
- Keep body paragraphs concise and factual.
- Do not mix footer lines into the body paragraph.
- Put footer items after one blank line following the body.
- Use one footer item per line.
- Do not insert blank lines between footer items.

## Provenance Footers

When a commit is ported, cherry-picked, squashed, or derived from another branch,
include provenance footers when known:

```text
Source-Branch: <branch>
Original-Commit: <sha> <title>
Related-Commit: <sha> <title>
```

For squashed commits, include one `Original-Commit:` footer per original commit.

## Before Committing

- Inspect staged changes before writing the message.
- Ensure the message describes the actual staged diff, not just the requested task.
- Do not include `Cargo.lock` or `src/rpc/src/protos_code_gen/` generated files unless
  the user explicitly asks.
