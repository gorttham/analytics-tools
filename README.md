# analytics-tools

A drop-in analytics toolkit for [Claude Code](https://claude.ai/code). Drop a dataset into `raw/`, run one command, and get a focused plain-English summary of your data, key insights, charts, and a shareable HTML report — no coding required.

---

## Requirements

- [Claude Code](https://claude.ai/code) (the CLI)
- Python 3.11+

---

## Quick start

**1. Clone the repo**

```bash
git clone https://github.com/gorttham/analytics-tools.git
cd analytics-tools
```

**2. Install dependencies**

```bash
pip install -e ".[dev]"
```

**3. Drop your data file into `raw/`**

Supported formats: CSV, Excel (`.xlsx`), JSON, Parquet.

```
raw/
  your-data.csv   ← put it here
```

**4. Open Claude Code and run**

```
/init-analytics
```

Claude will ask two quick questions — what you're trying to learn and what the data represents — then propose a focused investigation plan. Once you confirm, it profiles the data, surfaces goal-relevant insights, generates charts, and delivers a plain-English summary.

---

## How it works

Every `/init-analytics` session starts with a short intake conversation:

```
Claude: Before I dig into the data — what are you trying to learn from it?
You:    I want to know which products are underperforming by region.

Claude: Got it. What does this data represent?
You:    Daily retail sales across 4 regions.

Claude: Here's my plan of attack:
        → Compare sales and units by product across all regions
        → Flag products with consistently low sales or high discount dependency
        → Highlight regional outliers
        Does this match what you're after?
You:    Yes.

→ Analysis begins, focused on your goal.
```

Your goal and domain are saved to `.analytics/context.json` and used by every downstream step — profiling highlights the columns that matter, insights lead with what's relevant to your question, and charts are chosen to answer it directly.

---

## Skills (slash commands)

| Command | What it does |
|---|---|
| `/init-analytics` | Full pipeline: intake conversation → profile → insights → charts → summary |
| `/analytics:visualize` | Generate a specific chart or ask Claude to recommend one |
| `/analytics:report` | Save a self-contained HTML report of the session |
| `/analytics:improve` | Review and fix any logged errors or limitations |

### Examples

```
/analytics:visualize bar chart of sales by region
/analytics:visualize what's the best way to show customer age distribution?
/analytics:report
/analytics:improve
```

---

## Output

All generated files land in `output/` — safe to delete and regenerate at any time.

```
output/
  profile.json          # dataset shape, dtypes, nulls, stats
  cleaned.csv           # cleaned dataset (if you asked Claude to clean)
  charts/               # .html (interactive) and .png (static) charts
  reports/              # self-contained HTML report, safe to email or share
.analytics/
  context.json          # your stated goal and domain (persists across sessions)
```

`raw/` is read-only — your source files are never modified.

---

## Running tests

```bash
pytest tests/ -v
```

49 tests covering all five Python tools (profiler, cleaner, viz, report, feedback).

---

## Folder structure

```
.analytics/
  tools/        # Python scripts (profiler, cleaner, viz, report, feedback)
  agents/       # Claude agent definitions
  skills/       # Slash command definitions
  templates/    # HTML report template
  feedback/     # Append-only error/improvement log
raw/            # Drop input files here (read-only)
output/         # Generated charts and reports
tests/          # pytest test suite
```

---

## Supported chart types

`bar`, `line`, `scatter`, `histogram`, `heatmap`, `pie`, `box`

Interactive charts use Plotly (HTML). Static charts use matplotlib (PNG).
