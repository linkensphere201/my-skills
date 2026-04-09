---
name: exploratory-project-helper
description: Use this skill when the user is starting or shaping an exploratory project and needs help building background knowledge, organizing research notes, mapping open questions, or turning vague ideas into a structured investigation workflow. Do not use it for straightforward implementation-only tasks with already-clear requirements.
---

# Exploratory Project Helper

## When to Use
Use this skill when:
- The user is exploring a new domain, project, or problem space
- The task starts with background learning rather than implementation
- The user needs help organizing concepts, terminology, assumptions, and open questions
- The project is still in the research, framing, or discovery phase

Do not use this skill when:
- The task is a narrow implementation request with clear requirements
- The user only wants a one-off explanation without project structure
- The task is routine coding with no discovery workflow

## Quick Start
1. Read `references/workflow.md` for the standard exploratory workflow.
2. Read `references/doc-structure.md` when creating or updating project documents.
3. Read `references/pitfalls.md` if the project is ambiguous or repeatedly changing direction.
4. Use `scripts/init-exploratory-project.ps1` when the task is to initialize a fresh exploratory project folder from a standard structure.

## Core Rules
- Start with fact gathering and concept clarification before proposing solutions.
- Separate facts, assumptions, open questions, risks, and recommendations.
- Prefer building reusable project context over giving a one-time answer.
- Keep outputs concise and easy to scan.
- Update project documentation when the exploration changes future work.

## Workflow
1. Clarify the project theme and intended outcome.
2. Build a background knowledge base.
3. Create or update terminology, research notes, and question maps.
4. Identify the highest-impact unknowns.
5. Propose a short next-step plan based on current evidence.

## Reference Guide
- `references/workflow.md`: Standard exploratory workflow
- `references/doc-structure.md`: Recommended project documentation layout
- `references/pitfalls.md`: Common failure modes in exploratory work

## Scripted Path
If the task is to create a new exploratory project skeleton, run:
- `scripts/init-exploratory-project.ps1`
