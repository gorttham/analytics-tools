---
name: profile-dataset
description: Run a quick profiling pass on a dataset file or DataFrame in this repo — dtypes, nulls, cardinality, shape
---

# Profile Dataset

When invoked, perform the following steps:

1. **Identify the target** — ask the user which file or variable to profile if not specified. Accept CSV, Parquet, or JSON paths, or a named DataFrame in an open notebook.

2. **Read the data** — use pandas to load it. Print shape (rows × cols).

3. **Report per-column:**
   - dtype
   - null count + null %
   - unique value count (cardinality)
   - for numeric cols: min, max, mean, median, std
   - for string/object cols: top 3 most frequent values

4. **Flag anomalies:**
   - Columns with >30% nulls → label as "high null"
   - Columns with cardinality = 1 → label as "constant"
   - Columns with cardinality = row count → label as "likely ID"
   - Numeric columns where std = 0 → label as "zero variance"

5. **Suggest next steps** based on what you find — e.g. imputation candidates, columns to drop, type coercions needed.

Output the report as a clean markdown table, followed by the anomaly flags and suggestions.
