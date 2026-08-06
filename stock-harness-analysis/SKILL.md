---
name: stock-harness-analysis
description: Analyze A-share stocks, ETFs, indices, boards, custom groups, and the active StockHarness window group through the local read-only StockHarness MCP server. Use when the user asks to review the current workspace, compare watchlists or symbols, inspect board relationships, assess daily price/volume evidence, or evaluate tail-session provisional daily bars with explicit dates, sources, and uncertainty.
---

# StockHarness Analysis

Use the local `stock_harness` MCP server as the evidence layer for StockHarness-assisted market analysis. Keep all calls read-only and make the smallest set of calls that can answer the question.

## Resolve The Analysis Scope

1. Call `get_active_workspace` first when the user refers to the current workspace, open windows, visible charts, or "these symbols" without naming them.
2. Use the focused window, active window group, referenced symbols, list selections, attachments, chart ranges, indicators, and trend-line anchors to reconstruct the user's working context.
3. For a named symbol, group, board, ETF, or index, resolve it directly without reading the active workspace unless workspace context matters.
4. When a list drives another list or chart, treat the most recently focused source as the active relationship. Do not infer extra relationships beyond those returned by the server.

## Select MCP Tools

- Use instrument search and instrument detail tools to resolve names, symbols, types, and metadata.
- Use collection tools to list or inspect custom groups and their tagged members.
- Use board and membership tools to inspect board constituents, ETF holdings, or reverse board membership.
- Use latest-quote tools for a compact current snapshot.
- Use daily-bar tools only for an explicit date range and only for the symbols needed for the analysis.
- Prefer one bounded batch over repeated broad calls. Never request the whole market when the question concerns the active window group or a named collection.

## Apply Analysis Modes

### Active Workspace

Summarize the active group and focused window, then analyze only the referenced symbols relevant to the user's question. Preserve the distinction between fixed and linked windows.

### Custom Group

Read the group's members and tags first. Use tags such as emotion anchor, capacity anchor, sector leader, core recognition, or lagging catch-up as user-maintained hypotheses, not verified market facts.

### Board Or ETF

Resolve the board or ETF, inspect its members or holdings, and compare only representative names required by the question. State when membership data is missing, stale, or based on a disclosed ETF holding date.

### Multi-Symbol Comparison

Use the same date range and comparable fields for every symbol. Separate price structure, volume behavior, relative strength, and invalidation conditions.

### Tail-Session Provisional Bar

Treat an intraday daily bar as provisional. State its timestamp and source, and explain that high, low, close, volume, amount, indicators, and percentage change may still change before the final close. If the final daily store already covers that trade date, use the final record instead of the provisional record.

## Evidence Rules

- State the instrument name and symbol, evidence date, source, and whether the newest bar is final or intraday.
- Surface missing, stale, truncated, or unavailable data instead of silently substituting assumptions.
- Treat trend lines as symbol-owned user annotations. Use their anchors as context, but do not assign meaning from color or line style unless the user defined it.
- Separate observed data from interpretation. Phrase probability, sustainability, and market-regime judgments as inference.
- For comparisons, mention material listing-date or available-history differences.
- Do not present analysis as a guaranteed outcome or personalized trading instruction.

## Safety Boundaries

- Do not access StockHarness SQLite files, credentials, provider tokens, or the filesystem directly.
- Do not invoke write operations, mutate groups/layouts/drawings, or place trades.
- Do not start the StockHarness app implicitly. If the MCP server or active workspace is unavailable, report the bounded error and explain what context is missing.
- Do not expand a request into full-market collection or scanning unless the user explicitly asks for it and a bounded read-only tool supports it.

## Response Shape

Keep the answer compact and evidence-led:

1. Context and effective data date.
2. Observed price, volume, membership, or workspace evidence.
3. Interpretation and comparison.
4. Risks, uncertainty, and invalidation signals.
