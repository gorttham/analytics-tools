---
name: init-analytics
description: Run the full analytics pipeline on a dataset in raw/. Profiles, finds insights, and generates initial charts. Use at the start of any analytics session.
---

# /init-analytics

Run the full analytics pipeline. Follow these steps in order.

## Pre-flight Check

1. Verify at least one file exists in `raw/`. If not, respond: "Please drop a data file (CSV, Excel, JSON, or Parquet) into the `raw/` folder and run `/init-analytics` again."
2. Check Python dependencies:
   ```bash
   pip show pandas plotly matplotlib jinja2 openpyxl pyarrow 2>&1 | grep -c "^Name:"
   ```
   If the count is less than 6, run: `pip install -e ".[dev]"` from the project root.

## Pipeline

Execute each step using the corresponding agent. Wait for each to complete before proceeding.

**Step 0 — Understand the goal**
Use the `brainstormer` agent. Wait for `.analytics/context.json` to be written before proceeding.

**Step 1 — Profile the data**
Use the `profiler` agent.

**Step 2 — Find insights**
Use the `insight-finder` agent.

**Step 3 — Generate initial charts**
Use the `viz-recommender` agent. Instruct it: "Generate the 2–3 most informative charts for this dataset in open-ended mode."

**Step 4 — Deliver summary**
Present a single cohesive summary covering:
- What the dataset contains (filename, shape)
- Top 3–5 data quality observations
- Top 3–5 key insights, framed around the user's stated goal
- The charts generated and what each shows
- Suggested next steps (e.g. "Ask me to clean the data", "Run `/analytics:visualize` for a specific chart", "Run `/analytics:report` when ready")

Keep it readable. Plain English. No raw JSON.
