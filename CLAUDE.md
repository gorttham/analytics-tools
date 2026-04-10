# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

A reusable analytics toolkit designed to be dropped into any project. Core capabilities:
- **Dataset understanding** — profiling, schema inference, summary statistics, data type detection
- **Data cleaning** — missing value handling, outlier detection, normalization, deduplication
- **Intelligent visualization recommendation** — context-aware suggestion of chart types based on data shape, column semantics, and user-specified goals

## Architecture Principles

Tools in this repo are designed to be **composable and project-agnostic**:
- Each tool should work standalone (accepts a dataframe/path, returns results) and also compose with others via a pipeline interface
- Context about the dataset (domain, audience, goal) is passed explicitly — tools should not make silent assumptions
- Visualization recommendations are driven by heuristics + rules over the data profile, not hardcoded chart mappings

## Module Structure (intended)

```
analytics/
  profiling/    # Dataset understanding: dtypes, nulls, distributions, cardinality
  cleaning/     # Transforms: imputation, outlier handling, deduplication, type coercion
  recommender/  # Visual recommendation engine: scores chart types given data + context
  pipeline/     # Orchestrates profiling → cleaning → recommendation as a workflow
```

## Key Design Decisions

- **Input format**: Prefer pandas DataFrames as the primary interchange format; accept file paths (CSV, Parquet, JSON) at entry points only
- **Context object**: Visualization recommender accepts a `AnalyticsContext` (domain, goal, audience) to weight recommendations — this is the primary way to influence output without changing code
- **Output format**: Recommendations return ranked list of `(chart_type, rationale, config_hints)` tuples, not raw chart code

## Analytics Skills

This project includes a self-contained analytics toolkit in `.analytics/`. The following commands are available — when a user types one of these, read and follow the corresponding skill file:

| Command | Skill file |
|---|---|
| `/init-analytics` | `.analytics/skills/init-analytics/SKILL.md` |
| `/analytics:visualize` | `.analytics/skills/visualize/SKILL.md` |
| `/analytics:report` | `.analytics/skills/report/SKILL.md` |
| `/analytics:improve` | `.analytics/skills/improve/SKILL.md` |

Agents used by these skills live in `.analytics/agents/`. Python tools live in `.analytics/tools/`.

## Development Commands

```bash
pip install -e ".[dev]"
pytest tests/
ruff check .
```
