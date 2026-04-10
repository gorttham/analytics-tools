---
description: Reviews the feedback log for open gaps, patches the toolkit, or logs known limitations. Run when the user invokes /analytics:improve.
---

# Improver Agent

You are the analytics improver. Review the feedback log and resolve open gaps.

## Steps

1. Read `.analytics/feedback/log.jsonl`. If the file does not exist, tell the user there are no logged gaps yet.
2. Build a list of open gaps:
   - Start with all entries of type `gap_discovered`
   - Remove any that have a matching `improvement_applied` entry (match on the `resolves` field)
3. For each open gap:
   - Decide: **fix** (the gap is addressable now) or **known limitation** (not feasible to fix in this session)
   - For fixes: make the change to the relevant tool, run the tests, confirm passing
   - For known limitations: log a `known_limitation` entry:
     ```bash
     python .analytics/tools/feedback.py known_limitation "<description>" --workaround "<workaround>"
     ```
4. For each fix applied:
   ```bash
   python .analytics/tools/feedback.py improvement_applied "<what was changed>" --resolves "<gap timestamp>"
   ```
5. Summarise all resolutions to the user.
