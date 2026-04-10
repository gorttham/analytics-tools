# Brainstormer Agent — Design Spec
**Date:** 2026-04-10
**Status:** Approved

---

## Overview

Add a `brainstormer` agent to the analytics toolkit that runs at the start of `/init-analytics`. Before any data is touched, the agent asks the user two questions — their goal and the data's domain — proposes a focused investigation plan, and waits for confirmation. The confirmed context is written to `.analytics/context.json` and read by every downstream agent to frame their output around what the user actually wants to know.

---

## Motivation

The current `/init-analytics` pipeline is fully automatic: it profiles, finds insights, and generates charts without asking what the user cares about. This produces generic output — useful, but not focused. A sales analyst investigating regional underperformance and an HR manager looking for attrition patterns get the same analysis of the same dataset.

The brainstormer makes the analysis intentional: Claude understands the goal before it starts, and every downstream step — profiling, insights, visualisation — is shaped by that understanding.

---

## Conversation Flow

The brainstormer runs as part of `/init-analytics` before profiling begins.

### Step 1 — Ask goal
> "Before I dig into the data — what are you trying to learn from it? For example: spot anomalies, find underperformers, understand trends, compare groups…"

Wait for user response.

### Step 2 — Ask domain
> "Got it. What does this data represent — what's the business context? (e.g. retail transactions, monthly summaries, B2B sales…)"

Wait for user response.

### Step 3 — Propose focus
Based on goal + domain, Claude proposes 2–3 specific investigation angles in plain English:
> "Here's my plan of attack:
> → Compare **sales and units** by **product** across all regions
> → Look for products with consistently low sales or high discount dependency
> → Flag any regional patterns (a product underperforming in one region only)
>
> Does this match what you're after, or would you like to adjust the focus?"

Wait for confirmation or adjustment. If the user adjusts, revise the focus and confirm again.

### Step 4 — Write context.json
Once confirmed, write `.analytics/context.json`:
```json
{
  "goal": "<user's stated goal>",
  "domain": "<user's stated domain>",
  "focus": "<confirmed investigation focus>",
  "confirmed_by_user": true
}
```

### Re-run behaviour
If `context.json` already exists when `/init-analytics` runs, the brainstormer reads it and asks:
> "I have context from a previous session — goal: *[goal]*, domain: *[domain]*. Still working on the same thing, or would you like to update it?"

If the user says keep it, skip the full Q&A and proceed to profiling immediately.

---

## How Downstream Agents Use Context

Each agent reads `.analytics/context.json` at the start of its work if the file exists. Context is optional — agents must still work correctly without it.

| Agent | Behaviour with context |
|---|---|
| `profiler` | Flags goal-relevant columns prominently; notes if key columns appear to be missing for the stated goal |
| `insight-finder` | Leads with insights most relevant to the stated goal; frames observations in domain language |
| `viz-recommender` | Prioritises chart types and column combinations that best answer the stated goal |

---

## Files Changed

| File | Change |
|---|---|
| `.analytics/agents/brainstormer.md` | CREATE |
| `.analytics/skills/init-analytics/SKILL.md` | MODIFY — call brainstormer as Step 0 |
| `.analytics/agents/profiler.md` | MODIFY — read context.json, surface goal-relevant columns |
| `.analytics/agents/insight-finder.md` | MODIFY — frame insights around stated goal |
| `.analytics/agents/viz-recommender.md` | MODIFY — prioritise charts that answer the goal |

No Python tools change. No tests require updating.

---

## Data Flow

```
/init-analytics
  → brainstormer agent
      → asks goal (waits)
      → asks domain (waits)
      → proposes focus (waits for confirmation)
      → writes .analytics/context.json
  → profiler agent        (reads context.json)
  → insight-finder agent  (reads context.json)
  → viz-recommender agent (reads context.json)
  → summary delivered to user
```

---

## Out of Scope

- Audience question (kept simple for v1 — goal + domain is sufficient)
- Modifying the `cleaner`, `reporter`, or `improver` agents (context does not meaningfully change their behaviour)
- UI or report changes — the report already surfaces insights; context shapes what those insights say
