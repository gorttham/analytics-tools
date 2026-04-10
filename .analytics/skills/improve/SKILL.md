---
description: Review the analytics toolkit feedback log, triage open gaps, and improve the toolkit by patching tools or logging known limitations.
---

# /analytics:improve

Use the `improver` agent to review and address open gaps.

## Notes
- If `.analytics/feedback/log.jsonl` does not exist or is empty, tell the user: "No gaps have been logged yet. The toolkit logs issues automatically when tools encounter errors."
- After the improver finishes, present a summary: how many gaps were fixed, how many are now known limitations, and what was changed.
