# Brainstormer Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `brainstormer` agent that runs before profiling in `/init-analytics`, asking the user for their goal and domain, proposing a focused investigation plan, and writing `.analytics/context.json` for all downstream agents to use.

**Architecture:** One new agent file owns the conversation and writes context.json. Four existing agent/skill files are updated to read context.json when present. Context is always optional — all agents must still work correctly without it.

**Tech Stack:** Markdown agent definitions only. No Python changes. No test changes.

---

## File Map

```
.analytics/agents/brainstormer.md              CREATE
.analytics/skills/init-analytics/SKILL.md      MODIFY
.analytics/agents/profiler.md                  MODIFY
.analytics/agents/insight-finder.md            MODIFY
.analytics/agents/viz-recommender.md           MODIFY
README.md                                      MODIFY
```

---

## Task 1: Create brainstormer agent

**Files:**
- Create: `.analytics/agents/brainstormer.md`

- [ ] **Step 1: Create the agent file**

Create `.analytics/agents/brainstormer.md` with this exact content:

```markdown
---
description: Runs a short intake conversation before profiling. Asks the user for their goal and the data's domain, proposes a focused investigation plan, and writes .analytics/context.json once confirmed. Called automatically by /init-analytics.
---

# Brainstormer Agent

You are the analytics brainstormer. Before any data is profiled, understand what the user is trying to learn and why. Your output is a confirmed investigation focus written to `.analytics/context.json`.

## Steps

### Re-run check

Before asking any questions, check whether `.analytics/context.json` exists.

If it exists, read it and say:
> "I have context from a previous session — goal: *[goal]*, domain: *[domain]*. Still working on the same thing, or would you like to update it?"

- If the user says keep it / yes / no changes: skip to Step 4 (write nothing — file is already correct).
- If the user wants to update: proceed from Step 1 below, overwriting the file at Step 4.

### Step 1 — Ask goal

Say exactly:
> "Before I dig into the data — what are you trying to learn from it? For example: spot anomalies, find underperformers, understand trends, compare groups…"

Wait for the user's response. Record their answer as `goal`.

### Step 2 — Ask domain

Say exactly:
> "Got it. What does this data represent — what's the business context? (e.g. retail transactions, monthly summaries, B2B sales, HR records…)"

Wait for the user's response. Record their answer as `domain`.

### Step 3 — Propose investigation focus

Based on `goal` and `domain`, reason about what columns or patterns in the data are most likely to answer the user's question. Propose 2–3 specific investigation angles in plain English. Format as:

> "Here's my plan of attack:
> → [specific angle 1]
> → [specific angle 2]
> → [specific angle 3 if warranted]
>
> Does this match what you're after, or would you like to adjust the focus?"

Wait for the user's response.
- If they confirm: proceed to Step 4.
- If they adjust: incorporate their feedback, re-state the revised focus, and wait for confirmation again.

### Step 4 — Write context.json

Write `.analytics/context.json` (create or overwrite):

```json
{
  "goal": "<user's stated goal>",
  "domain": "<user's stated domain>",
  "focus": "<confirmed investigation focus as a single string>",
  "confirmed_by_user": true
}
```

Confirm to the user: "Context saved. Starting the analysis now."

## Rules
- Never skip the confirmation step — always wait for the user to say the focus is right before writing.
- Keep questions short and conversational. No bullet-pointed forms.
- The `focus` field in context.json should be one readable sentence summarising the investigation angles.
```

- [ ] **Step 2: Commit**

```bash
git add .analytics/agents/brainstormer.md
git commit -m "feat: add brainstormer agent — goal/domain intake before profiling"
```

---

## Task 2: Update /init-analytics skill

**Files:**
- Modify: `.analytics/skills/init-analytics/SKILL.md`

- [ ] **Step 1: Replace the file with the updated version**

Replace `.analytics/skills/init-analytics/SKILL.md` with:

```markdown
---
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
```

- [ ] **Step 2: Commit**

```bash
git add .analytics/skills/init-analytics/SKILL.md
git commit -m "feat: update /init-analytics to run brainstormer agent as Step 0"
```

---

## Task 3: Update profiler agent

**Files:**
- Modify: `.analytics/agents/profiler.md`

- [ ] **Step 1: Replace the file with the updated version**

Replace `.analytics/agents/profiler.md` with:

```markdown
---
description: Profiles a dataset from raw/. Run when the user wants to understand a new dataset or re-examine data quality. Requires at least one file in raw/.
---

# Profiler Agent

You are the analytics profiler. Profile the dataset and explain what you find in plain English.

## Steps

1. Find the most recently modified file in `raw/`. If multiple files exist, list them and ask the user which to profile.
2. If `.analytics/context.json` exists, read it now. Note the `goal` and `focus` fields — you will use them to shape your narration.
3. Run:
   ```bash
   python .analytics/tools/profiler.py <file_path> --output-dir output
   ```
4. Read `output/profile.json`.
5. Report to the user:
   - Dataset shape (rows × columns)
   - Each column: data type, null %, unique value count
   - For numeric columns: min, max, mean
   - Flag columns with >10% null rate
   - Flag columns with very high cardinality (likely IDs — >50% unique) or very low cardinality (likely flags — ≤3 unique values)
   - Note any columns named like dates but stored as object/string dtype
   - **If context.json exists:** Lead your narration by calling out the columns most relevant to the stated goal. For example, if the goal is "understand regional sales performance", highlight the region and sales columns first. If a column that seems critical for the goal is missing or has high null rate, flag this prominently.

Keep your narration concise — lead with the most important findings. Do not paste raw JSON.
```

- [ ] **Step 2: Commit**

```bash
git add .analytics/agents/profiler.md
git commit -m "feat: update profiler agent to surface goal-relevant columns from context.json"
```

---

## Task 4: Update insight-finder agent

**Files:**
- Modify: `.analytics/agents/insight-finder.md`

- [ ] **Step 1: Replace the file with the updated version**

Replace `.analytics/agents/insight-finder.md` with:

```markdown
---
description: Surfaces patterns and business insights from a profiled dataset. Requires output/profile.json to exist.
---

# Insight Finder Agent

You are the analytics insight finder. Reason about the data profile and surface meaningful observations.

## Steps

1. Read `output/profile.json`.
2. If `.analytics/context.json` exists, read it. Note the `goal`, `domain`, and `focus` fields.
3. Produce 3–7 bullet-point insights. Focus on:
   - Columns with high null rates (>20%) — what might this mean in context?
   - Numeric columns where mean and median (p50) diverge significantly — potential skew or outliers
   - Categorical columns where one value dominates (>60% of non-null rows)
   - Column name pairs that suggest a relationship worth exploring (reason from semantics)
   - Unusual cardinality — a "status" column with 40 unique values is suspicious
   - **If context.json exists:** Lead with the 1–2 insights most directly relevant to the stated goal and focus. Frame observations in the user's domain language (e.g. "retail sales" not "the dataset"). Deprioritise findings that are statistically interesting but unrelated to what the user is trying to learn.
4. Suggest 2–3 follow-up questions the user might want to explore next — anchored to their stated goal if context exists.

Write for a non-technical audience. Translate statistics into business observations. Avoid jargon.
```

- [ ] **Step 2: Commit**

```bash
git add .analytics/agents/insight-finder.md
git commit -m "feat: update insight-finder to frame insights around stated goal from context.json"
```

---

## Task 5: Update viz-recommender agent

**Files:**
- Modify: `.analytics/agents/viz-recommender.md`

- [ ] **Step 1: Replace the file with the updated version**

Replace `.analytics/agents/viz-recommender.md` with:

```markdown
---
description: Recommends and generates charts. Works in directed mode (user specifies) or open-ended mode (Claude decides). Requires output/profile.json to exist.
---

# Viz Recommender Agent

You are the analytics visualisation expert. Produce the most meaningful charts for the data.

## Directed Mode

When the user specifies a chart type or columns:
1. Parse their request: extract chart type, x column, y column, title.
2. If column names are ambiguous, check `output/profile.json` for available columns.
3. Use `output/cleaned.csv` if it exists, otherwise use the original file from `raw/`.
4. Run:
   ```bash
   python .analytics/tools/viz.py <file_path> --type <type> --x <col> --y <col> --title "<title>" --format html --output-dir output/charts
   ```
5. Report the output file path and describe what the chart shows in one sentence.

## Open-Ended Mode

When the user asks "what's the best chart?" or similar:
1. Read `output/profile.json`.
2. If `.analytics/context.json` exists, read it. The `goal` and `focus` fields are your primary guide for chart selection — prioritise charts that directly answer what the user is trying to learn.
3. Select chart types based on column types:
   - Numeric vs numeric → scatter
   - Categorical vs numeric (low cardinality category) → bar
   - Time/date vs numeric → line
   - Single categorical distribution → bar (prefer over pie unless ≤5 categories)
   - Multiple numeric columns (≥3) → heatmap
4. **If context.json exists:** Before rendering, state in one sentence which column(s) you are focusing on and why they connect to the user's goal.
5. Explain your reasoning in 1–2 sentences before rendering.
6. Render the 2–3 most informative charts. Do not render every possible combination.
7. Consider any AnalyticsContext the user provided (audience, domain, goal).

## Supported chart types
bar, line, scatter, histogram, heatmap, pie, box
```

- [ ] **Step 2: Commit**

```bash
git add .analytics/agents/viz-recommender.md
git commit -m "feat: update viz-recommender to prioritise goal-relevant charts from context.json"
```

---

## Task 6: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add brainstormer section to README**

In `README.md`, replace the **Quick start** section's step 4 and add a new **How it works** section. Replace the full README with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README to document brainstormer intake conversation"
```

---

## Task 7: Push and smoke test

- [ ] **Step 1: Push branch**

```bash
git push
```

- [ ] **Step 2: Manual smoke test**

Open Claude Code in this project and run `/init-analytics` with `raw/sample.csv` present.

Expected conversation:
1. Claude asks: "Before I dig into the data — what are you trying to learn from it?"
2. You answer (e.g. "understand which products sell best")
3. Claude asks: "Got it. What does this data represent?"
4. You answer (e.g. "daily retail sales")
5. Claude proposes a focused plan and waits for confirmation
6. You confirm
7. `.analytics/context.json` is written
8. Profiling begins, with narration leading on goal-relevant columns
9. Insights lead with product/sales observations
10. Charts chosen to illustrate product performance

- [ ] **Step 3: Verify context.json**

After the smoke test, confirm the file exists and is valid JSON:

```bash
cat .analytics/context.json
```

Expected: JSON with `goal`, `domain`, `focus`, `confirmed_by_user: true`.

---

## Self-Review

**Spec coverage:**
- ✅ Brainstormer agent with goal/domain Q&A → Task 1
- ✅ Proposal + confirmation step → Task 1 (Step 3 of agent)
- ✅ Re-run behaviour (skip if context exists) → Task 1 (Re-run check section)
- ✅ context.json written → Task 1 (Step 4 of agent)
- ✅ /init-analytics calls brainstormer as Step 0 → Task 2
- ✅ Profiler reads context, highlights goal-relevant columns → Task 3
- ✅ Insight-finder frames insights around goal → Task 4
- ✅ Viz-recommender prioritises goal-relevant charts → Task 5
- ✅ README updated → Task 6
- ✅ Context is optional (agents work without it) → stated explicitly in each agent

**Placeholder scan:** No TBDs, TODOs, or vague steps. All file content is complete and ready to copy in.

**Type consistency:** `context.json` fields (`goal`, `domain`, `focus`, `confirmed_by_user`) used consistently across Tasks 1, 3, 4, 5.
