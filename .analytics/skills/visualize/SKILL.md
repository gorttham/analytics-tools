---
description: Generate a chart from the current dataset. Accepts a specific request ("bar chart of X by Y") or an open-ended request ("show the best visualisation for these insights").
---

# /analytics:visualize

Use the `viz-recommender` agent to generate charts.

## Steps

1. If `output/profile.json` does not exist, use the `profiler` agent first, then proceed.
2. Pass the user's full request to the `viz-recommender` agent, including any context about audience or goal.
3. The viz-recommender handles both directed and open-ended requests automatically.

## Examples
- "Show me a bar chart of revenue by product category"
- "What's the best way to visualise the customer age distribution?"
- "Scatter plot of price vs rating, for an executive audience"
- "Show me the correlation between all numeric columns"
