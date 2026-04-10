# Analytics Toolkit — Design Spec
**Date:** 2026-04-10
**Status:** Approved

---

## Overview

A drop-in analytics toolkit for any project. Designed for non-technical users (product management, business teams) working with Claude Code. Users drop a dataset into `raw/`, run `/init-analytics`, and receive a plain-English summary of their data, initial insights, and charts. They can then ask follow-up questions and generate a shareable HTML report.

---

## Architecture

**Approach:** Specialized Agents Pipeline — skills are user-facing entry points; agents are Claude-driven workers that handle reasoning and narration; Python tools handle computation.

```
your-project/
  .analytics/
    skills/
      init-analytics/SKILL.md   # /init-analytics
      report/SKILL.md           # /analytics:report
      visualize/SKILL.md        # /analytics:visualize
      improve/SKILL.md          # /analytics:improve
    agents/
      profiler.md
      insight-finder.md
      cleaner.md
      viz-recommender.md
      reporter.md
      improver.md
    tools/
      profiler.py
      cleaner.py
      viz.py
      report.py
      feedback.py
    templates/
      report.html
    feedback/
      log.jsonl                 # unified audit log
  raw/                          # user drops input files here (read-only)
  output/
    charts/
    reports/
    profile.json
    cleaned.csv
```

**Rules:**
- `raw/` is read-only — tools never modify source files
- `output/` is fully regeneratable — safe to delete and re-run
- `.analytics/` is self-contained — no external config needed to activate

---

## Supported Input Formats

CSV, Excel (.xlsx), JSON, Parquet

---

## Skills (User-Facing Entry Points)

| Skill | Command | Description |
|---|---|---|
| `init-analytics` | `/init-analytics` | Full automatic pipeline: profile → insights → charts → narrated summary |
| `visualize` | `/analytics:visualize` | Request a specific chart or ask Claude to recommend the best visualization |
| `report` | `/analytics:report` | Assemble and save a self-contained HTML report of the session |
| `improve` | `/analytics:improve` | Review open gaps in `feedback/log.jsonl`, patch toolkit or log limitations |

---

## Agents

| Agent | Responsibility |
|---|---|
| `profiler` | Runs `profiler.py`, reads JSON output, narrates shape/quality findings in plain English |
| `insight-finder` | Reads the profile, reasons about patterns, correlations, anomalies — produces plain-English bullet points |
| `cleaner` | Runs `cleaner.py`, narrates what was changed and why, saves cleaned file to `output/` |
| `viz-recommender` | Decides which charts are meaningful (directed or autonomous), runs `viz.py`, confirms output saved |
| `reporter` | Collects all session outputs, runs `report.py`, confirms report path |
| `improver` | Reviews feedback log, decides fix vs. known-limitation, patches tools, writes log entry |

---

## Python Tools

| File | Responsibility |
|---|---|
| `profiler.py` | Load any supported format; infer dtypes; compute nulls, distributions, cardinality, basic stats; output `profile.json` |
| `cleaner.py` | Handle missing values, type coercion, outlier detection/removal, deduplication; return cleaned DataFrame + change log |
| `viz.py` | Accept dataset + chart spec (type, columns, title); render Plotly (interactive HTML) or matplotlib (static PNG); save to `output/charts/` |
| `report.py` | Inject charts, profile stats, insights, and data quality log into `templates/report.html`; save to `output/reports/report-YYYY-MM-DD.html` |
| `feedback.py` | Append structured entries to `feedback/log.jsonl` |

---

## Visualization

`/analytics:visualize` operates in two modes:
- **Directed** — user specifies chart type and columns ("bar chart of sales by region")
- **Open-ended** — user asks Claude to decide ("what's the best way to visualize these insights?"); viz-recommender reads `profile.json` + insights and selects autonomously, explaining its reasoning before rendering

Chart selection is influenced by `AnalyticsContext` (domain, audience, goal) when provided — e.g. an executive audience weights simple trend lines over correlation matrices. Context is supplied by the user as part of the skill invocation (e.g. `/analytics:visualize for an executive audience`) or stored in an optional `.analytics/context.json` file for session-wide defaults.

---

## Feedback & Improvement Loop

A unified append-only log at `.analytics/feedback/log.jsonl` tracks three entry types:

| Type | When | Who |
|---|---|---|
| `gap_discovered` | Error occurs or capability missing | `feedback.py` via PostToolUse hook, or Claude |
| `improvement_applied` | A fix is made to the toolkit | `improver` agent after patching |
| `known_limitation` | Triaged but not yet fixable | `improver` agent during review |

A `PostToolUse` hook in `.claude/settings.json` fires when any `.analytics/tools/*.py` script exits non-zero, automatically calling `feedback.py` with the error context.

Running `/analytics:improve` opens the full log, surfaces open gaps, and Claude decides whether to fix inline or log as a known limitation.

---

## Report Output

Self-contained HTML file (`output/reports/report-YYYY-MM-DD.html`) — no external dependencies, opens in any browser, safe to email or share.

**Sections:**
1. Header — dataset name, date, row/column count
2. Data Profile — dtype table, null summary, cardinality highlights
3. Key Insights — bullet-pointed findings from insight-finder
4. Charts — all charts generated during the session, with captions
5. Data Quality Log — changes made by cleaner (if run)
6. Limitations — any `known_limitation` entries from feedback log

---

## Data Flow

### Phase 1 — `/init-analytics` (automatic)
1. User drops file into `raw/`
2. User runs `/init-analytics`
3. Profiler agent → `profiler.py` → `output/profile.json`
4. Insight Finder agent → reads profile → narrates summary
5. Viz Recommender agent → picks 2-3 charts → `viz.py` → `output/charts/`
6. Claude delivers narrated summary + charts to user

### Phase 2 — Follow-up conversation (user-driven)
- Questions about data quality → Profiler agent
- Cleaning requests → Cleaner agent → `output/cleaned.csv`
- Chart requests → Viz Recommender agent → `output/charts/`
- Report request → Reporter agent → `output/reports/`

### Error / Gap path
1. Tool exits non-zero OR Claude hits capability gap
2. PostToolUse hook → `feedback.py` → `gap_discovered` logged
3. Claude explains issue and workaround to user
4. User or Claude runs `/analytics:improve` → Improver agent reviews and resolves

---

## Testing

Tests live in `tests/` mirroring the tools structure. All tests use real DataFrames — no mocking of pandas internals.

| Module | Coverage |
|---|---|
| `profiler.py` | Each supported format; invalid input handling |
| `cleaner.py` | Happy path + edge cases (all nulls, no nulls, single column) |
| `viz.py` | Each chart type renders without error; output file exists and is non-empty |
| `report.py` | Assembles correctly with partial inputs (no charts, no cleaning) |
| `feedback.py` | All 3 entry types write correctly to `log.jsonl` |

Agents and skills are validated manually using `raw/sample.csv` (included in toolkit).

---

## Out of Scope (v1)

- PDF export (known limitation — users can print HTML to PDF from browser)
- Real-time/streaming data sources
- Multi-dataset joins
- Authentication or access control
