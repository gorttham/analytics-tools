# Analytics Toolkit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a drop-in `.analytics/` toolkit that lets non-technical users analyse any dataset, gather insights, and produce shareable HTML reports using Claude Code.

**Architecture:** Specialized agents pipeline — Python tools handle computation (called as scripts), Claude agents handle reasoning and narration, skills are user-facing slash commands. All outputs land in `output/`; source data in `raw/` is never modified.

**Tech Stack:** Python 3.11+, pandas 2.x, plotly 5.x, matplotlib 3.x, jinja2 3.x, openpyxl, pyarrow, pytest, ruff

---

## File Map

```
pyproject.toml                                  CREATE
.gitignore                                      MODIFY
tests/conftest.py                               CREATE
tests/tools/__init__.py                         CREATE
tests/tools/test_utils.py                       CREATE
tests/tools/test_profiler.py                    CREATE
tests/tools/test_cleaner.py                     CREATE
tests/tools/test_viz.py                         CREATE
tests/tools/test_report.py                      CREATE
tests/tools/test_feedback.py                    CREATE
.analytics/tools/utils.py                       CREATE
.analytics/tools/profiler.py                    CREATE
.analytics/tools/cleaner.py                     CREATE
.analytics/tools/viz.py                         CREATE
.analytics/tools/report.py                      CREATE
.analytics/tools/feedback.py                    CREATE
.analytics/templates/report.html                CREATE
.analytics/agents/profiler.md                   CREATE
.analytics/agents/insight-finder.md             CREATE
.analytics/agents/cleaner.md                    CREATE
.analytics/agents/viz-recommender.md            CREATE
.analytics/agents/reporter.md                   CREATE
.analytics/agents/improver.md                   CREATE
.analytics/skills/init-analytics/SKILL.md       CREATE
.analytics/skills/report/SKILL.md               CREATE
.analytics/skills/visualize/SKILL.md            CREATE
.analytics/skills/improve/SKILL.md              CREATE
raw/sample.csv                                  CREATE
.claude/settings.json                           MODIFY (add PostToolUse hook)
```

---

## Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Modify: `.gitignore`
- Create: `tests/conftest.py`
- Create: `tests/tools/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "analytics-tools"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0",
    "openpyxl>=3.1",
    "pyarrow>=14.0",
    "plotly>=5.18",
    "matplotlib>=3.8",
    "jinja2>=3.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "ruff>=0.1",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
```

- [ ] **Step 2: Install dependencies**

Run: `pip install -e ".[dev]"`
Expected: Successfully installed analytics-tools and all dependencies with no errors.

- [ ] **Step 3: Create directory structure**

Run:
```bash
mkdir -p .analytics/tools .analytics/agents .analytics/skills/init-analytics .analytics/skills/report .analytics/skills/visualize .analytics/skills/improve .analytics/templates .analytics/feedback raw output/charts output/reports tests/tools
```

- [ ] **Step 4: Create conftest.py so tests can import tools directly**

Create `tests/conftest.py`:
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".analytics" / "tools"))
```

- [ ] **Step 5: Create __init__.py files**

Create `tests/__init__.py` (empty file).
Create `tests/tools/__init__.py` (empty file).

- [ ] **Step 6: Update .gitignore**

Add to `.gitignore`:
```
output/
.superpowers/
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
.eggs/
```

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml .gitignore tests/conftest.py tests/__init__.py tests/tools/__init__.py
git commit -m "chore: project setup — pyproject.toml, test structure, gitignore"
```

---

## Task 2: Shared Utilities (utils.py)

**Files:**
- Create: `.analytics/tools/utils.py`
- Create: `tests/tools/test_utils.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_utils.py`:
```python
import pandas as pd
import pytest

from utils import load_dataframe


def test_load_csv(tmp_path):
    path = tmp_path / "data.csv"
    pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}).to_csv(path, index=False)
    df = load_dataframe(path)
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_load_excel(tmp_path):
    path = tmp_path / "data.xlsx"
    pd.DataFrame({"a": [1, 2]}).to_excel(path, index=False)
    df = load_dataframe(path)
    assert list(df.columns) == ["a"]
    assert len(df) == 2


def test_load_json(tmp_path):
    path = tmp_path / "data.json"
    pd.DataFrame({"a": [1, 2]}).to_json(path, orient="records")
    df = load_dataframe(path)
    assert "a" in df.columns
    assert len(df) == 2


def test_load_parquet(tmp_path):
    path = tmp_path / "data.parquet"
    pd.DataFrame({"a": [1, 2]}).to_parquet(path, index=False)
    df = load_dataframe(path)
    assert list(df.columns) == ["a"]
    assert len(df) == 2


def test_load_invalid_type():
    with pytest.raises(TypeError, match="str or Path"):
        load_dataframe(123)


def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_dataframe("/nonexistent/file.csv")


def test_load_unsupported_format(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported format"):
        load_dataframe(path)
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/tools/test_utils.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'utils'`

- [ ] **Step 3: Implement utils.py**

Create `.analytics/tools/utils.py`:
```python
from pathlib import Path

import pandas as pd


def load_dataframe(source) -> pd.DataFrame:
    """Load a DataFrame from a file path.

    Args:
        source: Path to a CSV, Excel (.xlsx/.xls), JSON, or Parquet file.

    Returns:
        Loaded pandas DataFrame.

    Raises:
        TypeError: If source is not a str or Path.
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is not supported.
    """
    if not isinstance(source, (str, Path)):
        raise TypeError(f"source must be a str or Path, got {type(source).__name__}")
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    suffix = path.suffix.lower()
    loaders = {
        ".csv": pd.read_csv,
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".json": pd.read_json,
        ".parquet": pd.read_parquet,
    }
    if suffix not in loaders:
        raise ValueError(
            f"Unsupported format '{suffix}'. Supported: {sorted(loaders)}"
        )
    return loaders[suffix](path)
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/tools/test_utils.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add .analytics/tools/utils.py tests/tools/test_utils.py
git commit -m "feat: add utils.py with load_dataframe supporting CSV/Excel/JSON/Parquet"
```

---

## Task 3: Profiler Tool

**Files:**
- Create: `.analytics/tools/profiler.py`
- Create: `tests/tools/test_profiler.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_profiler.py`:
```python
import pandas as pd
import pytest

from profiler import profile_dataframe


@pytest.fixture
def mixed_df():
    return pd.DataFrame({
        "age": [25.0, 30.0, None, 45.0],
        "name": ["Alice", "Bob", "Charlie", "Alice"],
        "score": [88.5, 92.0, 76.5, None],
    })


def test_profile_shape(mixed_df):
    profile = profile_dataframe(mixed_df)
    assert profile["shape"]["rows"] == 4
    assert profile["shape"]["columns"] == 3


def test_profile_null_count(mixed_df):
    profile = profile_dataframe(mixed_df)
    assert profile["columns"]["age"]["null_count"] == 1
    assert profile["columns"]["age"]["null_pct"] == 25.0


def test_profile_numeric_stats(mixed_df):
    profile = profile_dataframe(mixed_df)
    stats = profile["columns"]["age"]["stats"]
    assert stats["min"] == 25.0
    assert stats["max"] == 45.0
    assert "mean" in stats


def test_profile_categorical_top_values(mixed_df):
    profile = profile_dataframe(mixed_df)
    top = profile["columns"]["name"]["top_values"]
    assert "Alice" in top
    assert top["Alice"] == 2


def test_profile_cardinality(mixed_df):
    profile = profile_dataframe(mixed_df)
    assert profile["columns"]["name"]["cardinality"] == 3


def test_profile_dtype_present(mixed_df):
    profile = profile_dataframe(mixed_df)
    assert "dtype" in profile["columns"]["age"]
    assert "float" in profile["columns"]["age"]["dtype"]


def test_profile_invalid_input():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        profile_dataframe({"not": "a dataframe"})
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/tools/test_profiler.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'profiler'`

- [ ] **Step 3: Implement profiler.py**

Create `.analytics/tools/profiler.py`:
```python
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_dataframe


def profile_dataframe(df: pd.DataFrame) -> dict:
    """Profile a DataFrame and return structured statistics.

    Args:
        df: DataFrame to profile.

    Returns:
        Dict with shape, column dtypes, null stats, cardinality, and distributions.

    Raises:
        TypeError: If df is not a pandas DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df).__name__}")

    print(
        f"Profiling DataFrame: columns={list(df.columns)}, dtypes={df.dtypes.to_dict()}",
        file=sys.stderr,
    )

    profile: dict = {
        "shape": {"rows": len(df), "columns": len(df.columns)},
        "columns": {},
    }

    for col in df.columns:
        series = df[col]
        col_info: dict = {
            "dtype": str(series.dtype),
            "null_count": int(series.isna().sum()),
            "null_pct": round(float(series.isna().mean()) * 100, 2),
            "cardinality": int(series.nunique()),
        }
        if pd.api.types.is_numeric_dtype(series):
            desc = series.describe()
            col_info["stats"] = {
                k: (round(float(desc[k]), 4) if not pd.isna(desc[k]) else None)
                for k in ("mean", "std", "min", "25%", "50%", "75%", "max")
            }
        else:
            top = series.value_counts().head(5)
            col_info["top_values"] = {str(k): int(v) for k, v in top.items()}

        profile["columns"][col] = col_info

    return profile


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile a dataset")
    parser.add_argument("input_file", help="Path to CSV, Excel, JSON, or Parquet file")
    parser.add_argument("--output-dir", default="output", help="Directory to write profile.json")
    args = parser.parse_args()

    df = load_dataframe(args.input_file)
    profile = profile_dataframe(df)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "profile.json"
    with open(output_path, "w") as f:
        json.dump(profile, f, indent=2)

    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/tools/test_profiler.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add .analytics/tools/profiler.py tests/tools/test_profiler.py
git commit -m "feat: add profiler.py — dtypes, nulls, cardinality, distributions"
```

---

## Task 4: Cleaner Tool

**Files:**
- Create: `.analytics/tools/cleaner.py`
- Create: `tests/tools/test_cleaner.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_cleaner.py`:
```python
import pandas as pd
import pytest

from cleaner import clean_dataframe


@pytest.fixture
def dirty_df():
    # Row 0 and 4 are duplicates; age and name have one null each
    return pd.DataFrame({
        "age": [25.0, 30.0, None, 45.0, 25.0],
        "name": ["Alice", "Bob", None, "Dave", "Alice"],
        "score": [88.5, 92.0, 76.5, 85.0, 88.5],
    })


def test_deduplication_removes_exact_duplicates(dirty_df):
    cleaned, log = clean_dataframe(dirty_df, impute_nulls=False, deduplicate=True)
    change = next(c for c in log["changes"] if c["type"] == "deduplication")
    assert change["rows_removed"] == 1
    assert len(cleaned) == len(dirty_df) - 1


def test_numeric_null_imputed_with_median(dirty_df):
    cleaned, log = clean_dataframe(dirty_df, impute_nulls=True, deduplicate=False)
    assert cleaned["age"].isna().sum() == 0
    change = next(
        c for c in log["changes"]
        if c["type"] == "null_imputation" and c["column"] == "age"
    )
    assert change["method"] == "median"
    assert change["nulls_filled"] == 1


def test_categorical_null_imputed_with_mode(dirty_df):
    cleaned, log = clean_dataframe(dirty_df, impute_nulls=True, deduplicate=False)
    assert cleaned["name"].isna().sum() == 0
    change = next(
        c for c in log["changes"]
        if c["type"] == "null_imputation" and c["column"] == "name"
    )
    assert change["method"] == "mode"


def test_original_dataframe_not_mutated(dirty_df):
    original_null_count = dirty_df["age"].isna().sum()
    clean_dataframe(dirty_df)
    assert dirty_df["age"].isna().sum() == original_null_count


def test_outlier_removal_with_3xiqr():
    df = pd.DataFrame({"value": [10.0, 11.0, 12.0, 10.0, 11.0, 1000.0]})
    cleaned, log = clean_dataframe(df, remove_outliers=True, deduplicate=False, impute_nulls=False)
    assert len(cleaned) == 5
    change = next(c for c in log["changes"] if c["type"] == "outlier_removal")
    assert change["rows_removed"] == 1
    assert change["method"] == "3xIQR"


def test_no_changes_when_already_clean():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": ["x", "y", "z"]})
    _, log = clean_dataframe(df)
    assert log["changes"] == []


def test_all_nulls_numeric_column_not_imputed():
    df = pd.DataFrame({"a": [None, None, None]})
    cleaned, _ = clean_dataframe(df, impute_nulls=True, deduplicate=False)
    # median of all-null is NaN — no valid fill value, column stays null
    assert cleaned["a"].isna().all()


def test_log_includes_final_shape(dirty_df):
    _, log = clean_dataframe(dirty_df)
    assert "final_shape" in log
    assert "rows" in log["final_shape"]


def test_invalid_input():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        clean_dataframe([1, 2, 3])
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/tools/test_cleaner.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'cleaner'`

- [ ] **Step 3: Implement cleaner.py**

Create `.analytics/tools/cleaner.py`:
```python
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_dataframe


def clean_dataframe(
    df: pd.DataFrame,
    impute_nulls: bool = True,
    remove_outliers: bool = False,
    deduplicate: bool = True,
) -> tuple[pd.DataFrame, dict]:
    """Clean a DataFrame by deduplicating, imputing nulls, and optionally removing outliers.

    Args:
        df: Input DataFrame. Never mutated.
        impute_nulls: Fill numeric nulls with column median; categorical with mode.
        remove_outliers: Remove rows where any numeric value falls outside 3×IQR.
        deduplicate: Drop exact duplicate rows.

    Returns:
        Tuple of (cleaned DataFrame, change_log dict).

    Raises:
        TypeError: If df is not a pandas DataFrame.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df).__name__}")

    print(
        f"Cleaning DataFrame: columns={list(df.columns)}, dtypes={df.dtypes.to_dict()}",
        file=sys.stderr,
    )

    result = df.copy()
    log: dict = {
        "original_shape": {"rows": len(df), "columns": len(df.columns)},
        "changes": [],
    }

    if deduplicate:
        before = len(result)
        result = result.drop_duplicates().reset_index(drop=True)
        removed = before - len(result)
        if removed > 0:
            log["changes"].append({"type": "deduplication", "rows_removed": removed})

    if impute_nulls:
        for col in result.columns:
            null_count = int(result[col].isna().sum())
            if null_count == 0:
                continue
            if pd.api.types.is_numeric_dtype(result[col]):
                fill_value = result[col].median()
                if pd.isna(fill_value):
                    continue  # all-null column — no valid median
                result[col] = result[col].fillna(fill_value)
                log["changes"].append({
                    "type": "null_imputation",
                    "column": col,
                    "method": "median",
                    "fill_value": round(float(fill_value), 4),
                    "nulls_filled": null_count,
                })
            else:
                mode = result[col].mode()
                if len(mode) == 0:
                    continue
                fill_value = mode.iloc[0]
                result[col] = result[col].fillna(fill_value)
                log["changes"].append({
                    "type": "null_imputation",
                    "column": col,
                    "method": "mode",
                    "fill_value": str(fill_value),
                    "nulls_filled": null_count,
                })

    if remove_outliers:
        numeric_cols = result.select_dtypes(include="number").columns
        mask = pd.Series(True, index=result.index)
        for col in numeric_cols:
            q1 = result[col].quantile(0.25)
            q3 = result[col].quantile(0.75)
            iqr = q3 - q1
            mask &= result[col].between(q1 - 3 * iqr, q3 + 3 * iqr)
        before = len(result)
        result = result[mask].reset_index(drop=True)
        removed = before - len(result)
        if removed > 0:
            log["changes"].append({
                "type": "outlier_removal",
                "method": "3xIQR",
                "rows_removed": removed,
            })

    log["final_shape"] = {"rows": len(result), "columns": len(result.columns)}
    return result, log


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean a dataset")
    parser.add_argument("input_file")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--remove-outliers", action="store_true")
    parser.add_argument("--no-dedup", action="store_true")
    args = parser.parse_args()

    df = load_dataframe(args.input_file)
    cleaned, log = clean_dataframe(
        df,
        impute_nulls=True,
        remove_outliers=args.remove_outliers,
        deduplicate=not args.no_dedup,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_dir / "cleaned.csv", index=False)
    with open(output_dir / "cleaning_log.json", "w") as f:
        json.dump(log, f, indent=2)

    print(json.dumps(log, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/tools/test_cleaner.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add .analytics/tools/cleaner.py tests/tools/test_cleaner.py
git commit -m "feat: add cleaner.py — null imputation, outlier removal, deduplication"
```

---

## Task 5: Viz Tool

**Files:**
- Create: `.analytics/tools/viz.py`
- Create: `tests/tools/test_viz.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_viz.py`:
```python
import matplotlib
matplotlib.use("Agg")  # must be set before any other matplotlib import

import pandas as pd
import pytest

from viz import render_chart, SUPPORTED_TYPES


@pytest.fixture
def numeric_df():
    return pd.DataFrame({
        "category": ["A", "B", "C", "A", "B"],
        "value": [10.0, 20.0, 15.0, 12.0, 18.0],
        "score": [1.0, 2.0, 3.0, 1.5, 2.5],
    })


def test_bar_chart_html_created(numeric_df, tmp_path):
    spec = {"type": "bar", "x": "category", "y": "value", "title": "Bar Test", "format": "html"}
    path = render_chart(numeric_df, spec, tmp_path)
    assert path.exists()
    assert path.suffix == ".html"
    assert path.stat().st_size > 0


def test_scatter_chart_html_created(numeric_df, tmp_path):
    spec = {"type": "scatter", "x": "value", "y": "score", "title": "Scatter Test", "format": "html"}
    path = render_chart(numeric_df, spec, tmp_path)
    assert path.exists()
    assert path.stat().st_size > 0


def test_histogram_html_created(numeric_df, tmp_path):
    spec = {"type": "histogram", "x": "value", "title": "Hist Test", "format": "html"}
    path = render_chart(numeric_df, spec, tmp_path)
    assert path.exists()


def test_heatmap_html_created(numeric_df, tmp_path):
    spec = {"type": "heatmap", "title": "Heatmap Test", "format": "html"}
    path = render_chart(numeric_df, spec, tmp_path)
    assert path.exists()


def test_bar_chart_png_created(numeric_df, tmp_path):
    spec = {"type": "bar", "x": "category", "y": "value", "title": "Bar PNG", "format": "png"}
    path = render_chart(numeric_df, spec, tmp_path)
    assert path.exists()
    assert path.suffix == ".png"
    assert path.stat().st_size > 0


def test_html_chart_contains_plotly_markup(numeric_df, tmp_path):
    spec = {"type": "bar", "x": "category", "y": "value", "title": "Bar Test", "format": "html"}
    path = render_chart(numeric_df, spec, tmp_path)
    content = path.read_text()
    assert "plotly" in content.lower()


def test_unsupported_chart_type_raises(numeric_df, tmp_path):
    spec = {"type": "donut", "title": "Bad", "format": "html"}
    with pytest.raises(ValueError, match="Unsupported chart type"):
        render_chart(numeric_df, spec, tmp_path)


def test_missing_column_raises(numeric_df, tmp_path):
    spec = {"type": "bar", "x": "nonexistent", "y": "value", "title": "Bad", "format": "html"}
    with pytest.raises(ValueError, match="Column 'nonexistent' not found"):
        render_chart(numeric_df, spec, tmp_path)


def test_heatmap_requires_two_numeric_columns(tmp_path):
    df = pd.DataFrame({"a": ["x", "y", "z"]})
    spec = {"type": "heatmap", "title": "Bad Heatmap", "format": "html"}
    with pytest.raises(ValueError, match="at least 2 numeric columns"):
        render_chart(df, spec, tmp_path)


def test_invalid_df_raises(tmp_path):
    with pytest.raises(TypeError, match="pandas DataFrame"):
        render_chart([1, 2, 3], {"type": "bar", "format": "html"}, tmp_path)
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/tools/test_viz.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'viz'`

- [ ] **Step 3: Implement viz.py**

Create `.analytics/tools/viz.py`:
```python
import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from utils import load_dataframe

SUPPORTED_TYPES = {"bar", "line", "scatter", "histogram", "heatmap", "pie", "box"}


def render_chart(df: pd.DataFrame, spec: dict, output_dir: Path) -> Path:
    """Render a chart from a DataFrame and save it to output_dir.

    Args:
        df: Source DataFrame.
        spec: Dict with keys:
            type (str): One of bar, line, scatter, histogram, heatmap, pie, box.
            x (str, optional): Column for x-axis.
            y (str, optional): Column for y-axis.
            title (str): Chart title.
            color (str, optional): Column for color grouping.
            format (str): 'html' for Plotly interactive, 'png' for matplotlib static.
        output_dir: Directory to save the chart file.

    Returns:
        Path to the saved chart file.

    Raises:
        TypeError: If df is not a pandas DataFrame.
        ValueError: If chart type is unsupported or a specified column is missing.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df).__name__}")

    chart_type = spec.get("type", "")
    if chart_type not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported chart type '{chart_type}'. Supported: {sorted(SUPPORTED_TYPES)}"
        )

    x = spec.get("x")
    y = spec.get("y")
    color = spec.get("color")
    title = spec.get("title", chart_type.capitalize())
    fmt = spec.get("format", "html")

    for col in [c for c in [x, y, color] if c is not None]:
        if col not in df.columns:
            raise ValueError(
                f"Column '{col}' not found in DataFrame. Available: {list(df.columns)}"
            )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{chart_type}_{x or 'auto'}_{timestamp}"

    if fmt == "html":
        return _render_plotly(df, chart_type, x, y, color, title, output_dir, stem)
    return _render_matplotlib(df, chart_type, x, y, title, output_dir, stem)


def _render_plotly(df, chart_type, x, y, color, title, output_dir, stem):
    import plotly.express as px

    if chart_type == "bar":
        fig = px.bar(df, x=x, y=y, title=title, color=color)
    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, title=title, color=color)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, title=title, color=color)
    elif chart_type == "histogram":
        fig = px.histogram(df, x=x, title=title, color=color)
    elif chart_type == "heatmap":
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if len(numeric_cols) < 2:
            raise ValueError("Heatmap requires at least 2 numeric columns")
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, title=title, text_auto=True, color_continuous_scale="RdBu_r")
    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y, title=title)
    elif chart_type == "box":
        fig = px.box(df, x=x, y=y, title=title, color=color)

    output_path = output_dir / f"{stem}.html"
    fig.write_html(str(output_path), include_plotlyjs="cdn", full_html=True)
    print(str(output_path))
    return output_path


def _render_matplotlib(df, chart_type, x, y, title, output_dir, stem):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))

    if chart_type == "bar":
        df.groupby(x)[y].mean().plot(kind="bar", ax=ax, title=title)
    elif chart_type == "line":
        df.plot(x=x, y=y, kind="line", ax=ax, title=title)
    elif chart_type == "scatter":
        df.plot.scatter(x=x, y=y, ax=ax, title=title)
    elif chart_type == "histogram":
        df[x].plot(kind="hist", ax=ax, title=title)
    elif chart_type == "heatmap":
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if len(numeric_cols) < 2:
            raise ValueError("Heatmap requires at least 2 numeric columns")
        corr = df[numeric_cols].corr()
        im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45)
        ax.set_yticklabels(corr.columns)
        plt.colorbar(im, ax=ax)
        ax.set_title(title)
    elif chart_type == "pie":
        df.groupby(x)[y].sum().plot(kind="pie", ax=ax, title=title, ylabel="")
    elif chart_type == "box":
        if x:
            df.boxplot(column=y, by=x, ax=ax)
        else:
            df[y].plot(kind="box", ax=ax)
        ax.set_title(title)
        plt.suptitle("")

    plt.tight_layout()
    output_path = output_dir / f"{stem}.png"
    fig.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(str(output_path))
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a chart from a dataset")
    parser.add_argument("input_file")
    parser.add_argument("--type", required=True, choices=sorted(SUPPORTED_TYPES))
    parser.add_argument("--x", default=None)
    parser.add_argument("--y", default=None)
    parser.add_argument("--title", default=None)
    parser.add_argument("--color", default=None)
    parser.add_argument("--format", choices=["html", "png"], default="html")
    parser.add_argument("--output-dir", default="output/charts")
    args = parser.parse_args()

    df = load_dataframe(args.input_file)
    spec = {
        "type": args.type,
        "x": args.x,
        "y": args.y,
        "title": args.title or args.type.capitalize(),
        "color": args.color,
        "format": args.format,
    }
    render_chart(df, spec, Path(args.output_dir))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/tools/test_viz.py -v`
Expected: 10 passed

- [ ] **Step 5: Commit**

```bash
git add .analytics/tools/viz.py tests/tools/test_viz.py
git commit -m "feat: add viz.py — bar, line, scatter, histogram, heatmap, pie, box (Plotly + matplotlib)"
```

---

## Task 6: Report Template and Tool

**Files:**
- Create: `.analytics/templates/report.html`
- Create: `.analytics/tools/report.py`
- Create: `tests/tools/test_report.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_report.py`:
```python
import json
from pathlib import Path

import pytest

from report import build_report


@pytest.fixture
def sample_profile():
    return {
        "shape": {"rows": 100, "columns": 3},
        "columns": {
            "age": {"dtype": "float64", "null_count": 5, "null_pct": 5.0, "cardinality": 80},
            "name": {"dtype": "object", "null_count": 0, "null_pct": 0.0, "cardinality": 95},
        },
    }


def test_report_creates_html_file(sample_profile, tmp_path):
    path = build_report(
        profile=sample_profile,
        insights=["Sales peaked in Q3", "High null rate in age"],
        chart_paths=[],
        output_dir=tmp_path,
    )
    assert path.exists()
    assert path.suffix == ".html"


def test_report_contains_insights(sample_profile, tmp_path):
    path = build_report(
        profile=sample_profile,
        insights=["Insight one", "Insight two"],
        chart_paths=[],
        output_dir=tmp_path,
    )
    content = path.read_text()
    assert "Insight one" in content
    assert "Insight two" in content


def test_report_contains_column_names(sample_profile, tmp_path):
    path = build_report(
        profile=sample_profile, insights=[], chart_paths=[], output_dir=tmp_path
    )
    content = path.read_text()
    assert "age" in content
    assert "name" in content


def test_report_with_limitations(sample_profile, tmp_path):
    path = build_report(
        profile=sample_profile,
        insights=[],
        chart_paths=[],
        limitations=["PDF export not supported"],
        output_dir=tmp_path,
    )
    assert "PDF export not supported" in path.read_text()


def test_report_with_cleaning_log(sample_profile, tmp_path):
    cleaning_log = {
        "changes": [
            {
                "type": "null_imputation",
                "column": "age",
                "method": "median",
                "fill_value": 35.0,
                "nulls_filled": 5,
            }
        ]
    }
    path = build_report(
        profile=sample_profile,
        insights=[],
        chart_paths=[],
        cleaning_log=cleaning_log,
        output_dir=tmp_path,
    )
    assert path.exists()
    assert path.stat().st_size > 0


def test_report_skips_nonexistent_charts(sample_profile, tmp_path):
    path = build_report(
        profile=sample_profile,
        insights=[],
        chart_paths=["/nonexistent/chart.html"],
        output_dir=tmp_path,
    )
    assert path.exists()


def test_report_invalid_profile(tmp_path):
    with pytest.raises(TypeError, match="dict"):
        build_report(profile="not a dict", insights=[], chart_paths=[], output_dir=tmp_path)


def test_report_missing_template(sample_profile, tmp_path, monkeypatch):
    import report as report_module
    monkeypatch.setattr(report_module, "_template_path", lambda: tmp_path / "missing.html")
    with pytest.raises(FileNotFoundError):
        build_report(profile=sample_profile, insights=[], chart_paths=[], output_dir=tmp_path)
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/tools/test_report.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'report'`

- [ ] **Step 3: Create the Jinja2 report template**

Create `.analytics/templates/report.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Analytics Report — {{ dataset_name }}</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 1100px; margin: 0 auto; padding: 2rem; color: #222; background: #fafafa; }
    h1 { color: #1a1a2e; border-bottom: 3px solid #6366f1; padding-bottom: 0.5rem; }
    h2 { color: #1a1a2e; margin-top: 2rem; }
    .meta { color: #666; font-size: 0.95rem; margin-bottom: 2rem; }
    table { border-collapse: collapse; width: 100%; margin: 1rem 0; background: #fff; }
    th, td { border: 1px solid #e0e0e0; padding: 0.6rem 1rem; text-align: left; font-size: 0.9rem; }
    th { background: #f0f0f8; font-weight: 600; }
    tr:hover { background: #f8f8ff; }
    .section { background: #fff; border: 1px solid #e0e0e0; border-left: 4px solid #6366f1; border-radius: 4px; padding: 1.5rem; margin: 1.5rem 0; }
    .insight-list { padding-left: 1.2rem; }
    .insight-list li { margin: 0.5rem 0; line-height: 1.6; }
    .chart-container { margin: 2rem 0; }
    .chart-title { font-weight: 600; margin-bottom: 0.5rem; color: #444; }
    .chart-frame { width: 100%; height: 480px; border: 1px solid #e0e0e0; border-radius: 4px; }
    .chart-img { max-width: 100%; border: 1px solid #e0e0e0; border-radius: 4px; }
    .change-log li { font-size: 0.9rem; color: #555; margin: 0.4rem 0; }
    .limitation { color: #c0392b; font-style: italic; font-size: 0.9rem; }
    .badge { display: inline-block; background: #6366f1; color: #fff; font-size: 0.75rem; padding: 0.2rem 0.6rem; border-radius: 999px; margin-left: 0.5rem; vertical-align: middle; }
  </style>
</head>
<body>
  <h1>Analytics Report <span class="badge">{{ report_date }}</span></h1>
  <p class="meta">
    <strong>Dataset:</strong> {{ dataset_name }} &nbsp;·&nbsp;
    <strong>Rows:</strong> {{ shape.rows }} &nbsp;·&nbsp;
    <strong>Columns:</strong> {{ shape.columns }}
  </p>

  <div class="section">
    <h2>Data Profile</h2>
    <table>
      <thead>
        <tr><th>Column</th><th>Type</th><th>Nulls</th><th>Null %</th><th>Unique Values</th></tr>
      </thead>
      <tbody>
        {% for col, info in columns.items() %}
        <tr>
          <td><strong>{{ col }}</strong></td>
          <td>{{ info.dtype }}</td>
          <td>{{ info.null_count }}</td>
          <td>{{ info.null_pct }}%</td>
          <td>{{ info.cardinality }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  {% if insights %}
  <div class="section">
    <h2>Key Insights</h2>
    <ul class="insight-list">
      {% for insight in insights %}
      <li>{{ insight }}</li>
      {% endfor %}
    </ul>
  </div>
  {% endif %}

  {% if charts %}
  <div class="section">
    <h2>Charts</h2>
    {% for chart in charts %}
    <div class="chart-container">
      <p class="chart-title">{{ chart.title }}</p>
      {% if chart.is_html %}
      <iframe class="chart-frame" src="data:text/html;base64,{{ chart.content }}" frameborder="0"></iframe>
      {% else %}
      <img class="chart-img" src="data:image/png;base64,{{ chart.content }}" alt="{{ chart.title }}">
      {% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}

  {% if cleaning_changes %}
  <div class="section">
    <h2>Data Quality Log</h2>
    <ul class="change-log">
      {% for change in cleaning_changes %}
      <li>
        <strong>{{ change.type | replace("_", " ") | title }}</strong>
        {% if change.column is defined %} — column <em>{{ change.column }}</em>{% endif %}
        {% if change.rows_removed is defined %}: {{ change.rows_removed }} rows removed{% endif %}
        {% if change.nulls_filled is defined %}: {{ change.nulls_filled }} nulls filled using {{ change.method }} → {{ change.fill_value }}{% endif %}
      </li>
      {% endfor %}
    </ul>
  </div>
  {% endif %}

  {% if limitations %}
  <div class="section">
    <h2>Known Limitations</h2>
    <ul>
      {% for lim in limitations %}
      <li class="limitation">{{ lim }}</li>
      {% endfor %}
    </ul>
  </div>
  {% endif %}
</body>
</html>
```

- [ ] **Step 4: Implement report.py**

Create `.analytics/tools/report.py`:
```python
import argparse
import base64
import json
import sys
from datetime import date
from pathlib import Path

from jinja2 import Template


def _template_path() -> Path:
    return Path(__file__).parent.parent / "templates" / "report.html"


def build_report(
    profile: dict,
    insights: list[str],
    chart_paths: list[str],
    cleaning_log: dict | None = None,
    limitations: list[str] | None = None,
    dataset_name: str = "dataset",
    output_dir: Path = Path("output/reports"),
) -> Path:
    """Assemble a self-contained HTML analytics report.

    Args:
        profile: Dict produced by profiler.py (output/profile.json).
        insights: List of plain-English insight strings.
        chart_paths: List of paths to .html or .png chart files.
        cleaning_log: Dict from cleaning_log.json (optional).
        limitations: List of known limitation strings (optional).
        dataset_name: Human-readable name shown in the report header.
        output_dir: Directory where the report file is saved.

    Returns:
        Path to the saved HTML report.

    Raises:
        TypeError: If profile is not a dict.
        FileNotFoundError: If the report template is missing.
    """
    if not isinstance(profile, dict):
        raise TypeError(f"profile must be a dict, got {type(profile).__name__}")

    tmpl_path = _template_path()
    if not tmpl_path.exists():
        raise FileNotFoundError(f"Report template not found: {tmpl_path}")

    template = Template(tmpl_path.read_text(encoding="utf-8"))

    charts = []
    for raw_path in (chart_paths or []):
        p = Path(raw_path)
        if not p.exists():
            continue
        if p.suffix == ".html":
            b64 = base64.b64encode(p.read_bytes()).decode()
            charts.append({"title": p.stem.replace("_", " ").title(), "is_html": True, "content": b64})
        elif p.suffix == ".png":
            b64 = base64.b64encode(p.read_bytes()).decode()
            charts.append({"title": p.stem.replace("_", " ").title(), "is_html": False, "content": b64})

    html = template.render(
        dataset_name=dataset_name,
        report_date=date.today().isoformat(),
        shape=profile.get("shape", {"rows": 0, "columns": 0}),
        columns=profile.get("columns", {}),
        insights=insights or [],
        charts=charts,
        cleaning_changes=(cleaning_log or {}).get("changes", []),
        limitations=limitations or [],
    )

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"report-{date.today().isoformat()}.html"
    output_path.write_text(html, encoding="utf-8")
    print(str(output_path))
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble an HTML analytics report")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--dataset-name", default="dataset")
    parser.add_argument("--insights", nargs="*", default=[])
    parser.add_argument("--charts", nargs="*", default=[])
    parser.add_argument("--cleaning-log", default=None)
    parser.add_argument("--limitations", nargs="*", default=[])
    parser.add_argument("--output-dir", default="output/reports")
    args = parser.parse_args()

    with open(args.profile) as f:
        profile = json.load(f)

    cleaning_log = None
    if args.cleaning_log:
        with open(args.cleaning_log) as f:
            cleaning_log = json.load(f)

    build_report(
        profile=profile,
        insights=args.insights,
        chart_paths=args.charts or [],
        cleaning_log=cleaning_log,
        limitations=args.limitations or [],
        dataset_name=args.dataset_name,
        output_dir=Path(args.output_dir),
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests — note the monkeypatch test**

The `test_report_missing_template` test uses `monkeypatch` on `_template_path`. Since we exposed it as a module-level function, update the test to patch it correctly:

In `tests/tools/test_report.py`, the monkeypatch test should read:
```python
def test_report_missing_template(sample_profile, tmp_path, monkeypatch):
    import report as report_module
    monkeypatch.setattr(report_module, "_template_path", lambda: tmp_path / "missing.html")
    with pytest.raises(FileNotFoundError):
        build_report(profile=sample_profile, insights=[], chart_paths=[], output_dir=tmp_path)
```
(This is already written correctly above — no change needed.)

Run: `pytest tests/tools/test_report.py -v`
Expected: 8 passed

- [ ] **Step 6: Commit**

```bash
git add .analytics/tools/report.py .analytics/templates/report.html tests/tools/test_report.py
git commit -m "feat: add report.py and report.html template — self-contained HTML report assembly"
```

---

## Task 7: Feedback Tool and PostToolUse Hook

**Files:**
- Create: `.analytics/tools/feedback.py`
- Create: `tests/tools/test_feedback.py`
- Modify: `.claude/settings.json`
- Create: `.analytics/feedback/.gitkeep`

- [ ] **Step 1: Write the failing tests**

Create `tests/tools/test_feedback.py`:
```python
import json
from pathlib import Path

import pytest

from feedback import append_log_entry, make_entry, VALID_TYPES


def test_gap_discovered_written(tmp_path):
    log_path = tmp_path / "log.jsonl"
    entry = make_entry("gap_discovered", "user asked for geospatial map", severity="high")
    append_log_entry(entry, log_path)
    saved = json.loads(log_path.read_text().strip())
    assert saved["type"] == "gap_discovered"
    assert saved["context"] == "user asked for geospatial map"
    assert saved["severity"] == "high"
    assert "timestamp" in saved


def test_improvement_applied_written(tmp_path):
    log_path = tmp_path / "log.jsonl"
    entry = make_entry("improvement_applied", "added box plot support to viz.py")
    append_log_entry(entry, log_path)
    saved = json.loads(log_path.read_text().strip())
    assert saved["type"] == "improvement_applied"


def test_known_limitation_written_with_workaround(tmp_path):
    log_path = tmp_path / "log.jsonl"
    entry = make_entry("known_limitation", "PDF export not supported", workaround="print to PDF from browser")
    append_log_entry(entry, log_path)
    saved = json.loads(log_path.read_text().strip())
    assert saved["type"] == "known_limitation"
    assert saved["workaround"] == "print to PDF from browser"


def test_multiple_entries_append_not_overwrite(tmp_path):
    log_path = tmp_path / "log.jsonl"
    for i in range(3):
        append_log_entry(make_entry("gap_discovered", f"gap {i}"), log_path)
    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 3


def test_creates_parent_directories(tmp_path):
    log_path = tmp_path / "nested" / "dir" / "log.jsonl"
    append_log_entry(make_entry("gap_discovered", "test"), log_path)
    assert log_path.exists()


def test_invalid_entry_type_raises(tmp_path):
    log_path = tmp_path / "log.jsonl"
    with pytest.raises(ValueError, match="gap_discovered"):
        append_log_entry({"type": "unknown_type", "context": "test"}, log_path)


def test_entry_not_dict_raises(tmp_path):
    log_path = tmp_path / "log.jsonl"
    with pytest.raises(TypeError, match="dict"):
        append_log_entry("not a dict", log_path)


def test_none_kwargs_excluded_from_entry():
    entry = make_entry("gap_discovered", "test", severity=None, resolves=None)
    assert "severity" not in entry
    assert "resolves" not in entry
```

- [ ] **Step 2: Run tests to confirm they fail**

Run: `pytest tests/tools/test_feedback.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'feedback'`

- [ ] **Step 3: Implement feedback.py**

Create `.analytics/tools/feedback.py`:
```python
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

VALID_TYPES = {"gap_discovered", "improvement_applied", "known_limitation"}


def make_entry(entry_type: str, context: str, **kwargs) -> dict:
    """Build a log entry dict with a UTC timestamp.

    Args:
        entry_type: One of gap_discovered, improvement_applied, known_limitation.
        context: Human-readable description.
        **kwargs: Optional fields: severity, resolves, workaround, detail.
                  Keys with None values are excluded.

    Returns:
        Entry dict ready to pass to append_log_entry.
    """
    entry = {
        "type": entry_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": context,
    }
    entry.update({k: v for k, v in kwargs.items() if v is not None})
    return entry


def append_log_entry(entry: dict, log_path: Path) -> None:
    """Append a structured entry to the feedback log.

    Args:
        entry: Dict with at least 'type' and 'context' keys.
        log_path: Path to the JSONL log file (created if missing).

    Raises:
        TypeError: If entry is not a dict.
        ValueError: If entry type is not a valid VALID_TYPES value.
    """
    if not isinstance(entry, dict):
        raise TypeError(f"entry must be a dict, got {type(entry).__name__}")
    if entry.get("type") not in VALID_TYPES:
        raise ValueError(
            f"entry type must be one of {sorted(VALID_TYPES)}, got '{entry.get('type')}'"
        )
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Append an entry to the analytics feedback log")
    parser.add_argument("type", choices=sorted(VALID_TYPES))
    parser.add_argument("context", help="Description of the gap, improvement, or limitation")
    parser.add_argument("--detail", default=None)
    parser.add_argument("--severity", choices=["low", "medium", "high"], default=None)
    parser.add_argument("--resolves", default=None, help="Timestamp of gap_discovered this resolves")
    parser.add_argument("--workaround", default=None)
    parser.add_argument("--log-path", default=".analytics/feedback/log.jsonl")
    args = parser.parse_args()

    entry = make_entry(
        args.type,
        args.context,
        detail=args.detail,
        severity=args.severity,
        resolves=args.resolves,
        workaround=args.workaround,
    )
    append_log_entry(entry, Path(args.log_path))
    print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to confirm they pass**

Run: `pytest tests/tools/test_feedback.py -v`
Expected: 8 passed

- [ ] **Step 5: Add PostToolUse hook to .claude/settings.json**

Replace `.claude/settings.json` with:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Bash(python:*)",
      "Bash(pip:*)",
      "Bash(pytest:*)",
      "Bash(ruff:*)"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python -c \"\nimport json, sys, subprocess\ndata = json.load(sys.stdin)\nif data.get('tool_name') != 'Bash':\n    sys.exit(0)\ncmd = data.get('tool_input', {}).get('command', '')\nif '.analytics/tools/' not in cmd or not cmd.strip().startswith('python'):\n    sys.exit(0)\nresponse = data.get('tool_response', {})\nif isinstance(response, dict) and response.get('exit_code', 0) == 0:\n    sys.exit(0)\ncontext = cmd[:200].replace('\\\"', '\\\\\\\"')\nsubprocess.run(['python', '.analytics/tools/feedback.py', 'gap_discovered', context, '--severity', 'medium', '--detail', 'non-zero exit from analytics tool'], capture_output=True)\n\""
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 6: Create feedback directory placeholder**

Run: `touch .analytics/feedback/.gitkeep`

- [ ] **Step 7: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass.

- [ ] **Step 8: Commit**

```bash
git add .analytics/tools/feedback.py tests/tools/test_feedback.py .analytics/feedback/.gitkeep .claude/settings.json
git commit -m "feat: add feedback.py, PostToolUse hook for automatic gap logging"
```

---

## Task 8: Agents

**Files:**
- Create: `.analytics/agents/profiler.md`
- Create: `.analytics/agents/insight-finder.md`
- Create: `.analytics/agents/cleaner.md`
- Create: `.analytics/agents/viz-recommender.md`
- Create: `.analytics/agents/reporter.md`
- Create: `.analytics/agents/improver.md`

- [ ] **Step 1: Create profiler agent**

Create `.analytics/agents/profiler.md`:
```markdown
---
description: Profiles a dataset from raw/. Run when the user wants to understand a new dataset or re-examine data quality. Requires at least one file in raw/.
---

# Profiler Agent

You are the analytics profiler. Profile the dataset and explain what you find in plain English.

## Steps

1. Find the most recently modified file in `raw/`. If multiple files exist, list them and ask the user which to profile.
2. Run:
   ```bash
   python .analytics/tools/profiler.py <file_path> --output-dir output
   ```
3. Read `output/profile.json`.
4. Report to the user:
   - Dataset shape (rows × columns)
   - Each column: data type, null %, unique value count
   - For numeric columns: min, max, mean
   - Flag columns with >10% null rate
   - Flag columns with very high cardinality (likely IDs — >50% unique) or very low cardinality (likely flags — ≤3 unique values)
   - Note any columns named like dates but stored as object/string dtype

Keep your narration concise — lead with the most important findings. Do not paste raw JSON.
```

- [ ] **Step 2: Create insight-finder agent**

Create `.analytics/agents/insight-finder.md`:
```markdown
---
description: Surfaces patterns and business insights from a profiled dataset. Requires output/profile.json to exist.
---

# Insight Finder Agent

You are the analytics insight finder. Reason about the data profile and surface meaningful observations.

## Steps

1. Read `output/profile.json`.
2. Produce 3–7 bullet-point insights. Focus on:
   - Columns with high null rates (>20%) — what might this mean in context?
   - Numeric columns where mean and median (p50) diverge significantly — potential skew or outliers
   - Categorical columns where one value dominates (>60% of non-null rows)
   - Column name pairs that suggest a relationship worth exploring (reason from semantics)
   - Unusual cardinality — a "status" column with 40 unique values is suspicious
3. Suggest 2–3 follow-up questions the user might want to explore next.

Write for a non-technical audience. Translate statistics into business observations. Avoid jargon.
```

- [ ] **Step 3: Create cleaner agent**

Create `.analytics/agents/cleaner.md`:
```markdown
---
description: Cleans a dataset. Handles null imputation, outlier removal, and deduplication. Requires output/profile.json to exist.
---

# Cleaner Agent

You are the analytics cleaner. Clean the dataset and explain every change made.

## Steps

1. Read `output/profile.json` to understand what needs cleaning.
2. Choose flags:
   - Add `--remove-outliers` only if the user requested it or if numeric distributions look highly skewed (mean much larger than median)
   - Deduplication is on by default; add `--no-dedup` only if the user asks
3. Run (use the original file from `raw/`, not `output/cleaned.csv`, unless the user asks to re-clean):
   ```bash
   python .analytics/tools/cleaner.py <raw_file_path> --output-dir output [--remove-outliers]
   ```
4. Read the JSON output from stdout (the change log).
5. Report to the user:
   - How many duplicates were removed (if any)
   - Which columns had nulls filled, the fill value, and the method (median/mode)
   - How many outlier rows were removed (if applicable)
   - Original shape → final shape
6. Tell the user the cleaned file is at `output/cleaned.csv`.
```

- [ ] **Step 4: Create viz-recommender agent**

Create `.analytics/agents/viz-recommender.md`:
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
2. Select chart types based on column types:
   - Numeric vs numeric → scatter
   - Categorical vs numeric (low cardinality category) → bar
   - Time/date vs numeric → line
   - Single categorical distribution → bar (prefer over pie unless ≤5 categories)
   - Multiple numeric columns (≥3) → heatmap
3. Explain your reasoning in 1–2 sentences before rendering.
4. Render the 2–3 most informative charts. Do not render every possible combination.
5. Consider any AnalyticsContext the user provided (audience, domain, goal).

## Supported chart types
bar, line, scatter, histogram, heatmap, pie, box
```

- [ ] **Step 5: Create reporter agent**

Create `.analytics/agents/reporter.md`:
```markdown
---
description: Assembles the final HTML analytics report from all session outputs. Run when the user asks for a report.
---

# Reporter Agent

You are the analytics reporter. Assemble all session outputs into a shareable HTML report.

## Steps

1. Verify `output/profile.json` exists. If not, tell the user to run `/init-analytics` first.
2. Collect available outputs:
   - Charts: all `.html` and `.png` files in `output/charts/` — list them
   - Cleaning log: `output/cleaning_log.json` (optional)
   - Known limitations: read `.analytics/feedback/log.jsonl` (if it exists) and extract `known_limitation` entries with no matching `improvement_applied`
   - Dataset name: use the source filename from `raw/` (without extension)
3. Ask the user: "Would you like to add any final insights to the report, or should I use the insights from our session?"
4. Once confirmed, run:
   ```bash
   python .analytics/tools/report.py \
     --profile output/profile.json \
     --dataset-name "<name>" \
     --insights "<insight1>" "<insight2>" \
     --charts output/charts/chart1.html output/charts/chart2.html \
     --cleaning-log output/cleaning_log.json \
     --limitations "<limitation1>" \
     --output-dir output/reports
   ```
   Omit `--cleaning-log` if cleaning was not run. Omit `--limitations` if log is empty.
5. Tell the user the report is saved at `output/reports/report-YYYY-MM-DD.html` and can be opened in any browser or emailed as an attachment.
```

- [ ] **Step 6: Create improver agent**

Create `.analytics/agents/improver.md`:
```markdown
---
description: Reviews the feedback log for open gaps and patches the toolkit or logs known limitations.
---

# Improver Agent

You are the analytics toolkit improver. Address open gaps in the feedback log.

## Steps

1. Read `.analytics/feedback/log.jsonl`. If it does not exist or is empty, tell the user there are no gaps logged yet and stop.
2. Parse all entries. Find `gap_discovered` entries that have no matching `improvement_applied` entry (match by checking `resolves` field against the gap's `timestamp`).
3. For each open gap, decide:
   - **Can fix now** (tool capability gap, missing chart type, wrong output format): implement the fix in `.analytics/tools/`, run the relevant test, then log:
     ```bash
     python .analytics/tools/feedback.py improvement_applied "<description of fix>" --resolves "<original gap timestamp>"
     ```
   - **Cannot fix now** (external dependency, out of scope, requires new library): log as known limitation:
     ```bash
     python .analytics/tools/feedback.py known_limitation "<description>" --workaround "<workaround if applicable>"
     ```
4. After processing all gaps, summarise: N gaps fixed, N deferred as known limitations, list of what was done.

## Rules
- Never delete or modify existing entries in `log.jsonl` — it is append-only.
- Only modify files in `.analytics/tools/` and `.analytics/templates/`.
- After modifying a tool, run its tests:
  ```bash
  pytest tests/tools/test_<tool_name>.py -v
  ```
```

- [ ] **Step 7: Commit**

```bash
git add .analytics/agents/
git commit -m "feat: add 6 analytics agents — profiler, insight-finder, cleaner, viz-recommender, reporter, improver"
```

---

## Task 9: Skills

**Files:**
- Create: `.analytics/skills/init-analytics/SKILL.md`
- Create: `.analytics/skills/report/SKILL.md`
- Create: `.analytics/skills/visualize/SKILL.md`
- Create: `.analytics/skills/improve/SKILL.md`

- [ ] **Step 1: Create /init-analytics skill**

Create `.analytics/skills/init-analytics/SKILL.md`:
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
- Top 3–5 key insights
- The charts generated and what each shows
- Suggested next steps (e.g. "Ask me to clean the data", "Run `/analytics:visualize` for a specific chart", "Run `/analytics:report` when ready")

Keep it readable. Plain English. No raw JSON.
```

- [ ] **Step 2: Create /analytics:visualize skill**

Create `.analytics/skills/visualize/SKILL.md`:
```markdown
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
```

- [ ] **Step 3: Create /analytics:report skill**

Create `.analytics/skills/report/SKILL.md`:
```markdown
---
description: Assemble and save a full HTML analytics report of the current session. Opens in any browser and can be shared as a file.
---

# /analytics:report

Use the `reporter` agent to assemble the report.

After the report is saved, remind the user:
- Open it in any browser: `output/reports/report-YYYY-MM-DD.html`
- To export as PDF: use the browser's Print → Save as PDF function
- The file is self-contained and can be emailed or shared directly
```

- [ ] **Step 4: Create /analytics:improve skill**

Create `.analytics/skills/improve/SKILL.md`:
```markdown
---
description: Review the analytics toolkit feedback log, triage open gaps, and improve the toolkit by patching tools or logging known limitations.
---

# /analytics:improve

Use the `improver` agent to review and address open gaps.

## Notes
- If `.analytics/feedback/log.jsonl` does not exist or is empty, tell the user: "No gaps have been logged yet. The toolkit logs issues automatically when tools encounter errors."
- After the improver finishes, present a summary: how many gaps were fixed, how many are now known limitations, and what was changed.
```

- [ ] **Step 5: Commit**

```bash
git add .analytics/skills/
git commit -m "feat: add 4 analytics skills — init-analytics, visualize, report, improve"
```

---

## Task 10: Sample Data and Smoke Test

**Files:**
- Create: `raw/sample.csv`

- [ ] **Step 1: Create sample.csv**

Create `raw/sample.csv`:
```csv
date,region,product,sales,units,customer_age,customer_segment,discount_pct
2024-01-10,North,Widget A,1250.00,5,34,Enterprise,0.10
2024-01-10,South,Widget B,890.50,3,,SMB,0.05
2024-01-11,East,Widget A,2100.00,8,45,Enterprise,0.15
2024-01-11,West,Widget C,430.00,2,29,Startup,0.00
2024-01-12,North,Widget B,1780.00,6,38,SMB,0.05
2024-01-12,South,Widget A,950.00,4,,Enterprise,0.10
2024-01-13,East,Widget C,620.00,3,52,Enterprise,0.00
2024-01-13,West,Widget A,1890.00,7,31,SMB,0.10
2024-01-14,North,Widget B,2340.00,9,41,Enterprise,0.20
2024-01-14,South,Widget C,510.00,2,27,Startup,0.00
2024-01-15,East,Widget A,1670.00,6,36,SMB,0.05
2024-01-15,West,Widget B,980.00,4,,Enterprise,0.10
2024-01-16,North,Widget C,750.00,3,48,Enterprise,0.00
2024-01-16,South,Widget A,1420.00,5,33,SMB,0.10
2024-01-17,East,Widget B,1890.00,7,44,Enterprise,0.15
2024-01-17,West,Widget A,2250.00,8,39,Startup,0.05
2024-01-18,North,Widget C,630.00,2,,SMB,0.00
2024-01-18,South,Widget B,1560.00,6,42,Enterprise,0.10
2024-01-19,East,Widget A,1980.00,7,35,Enterprise,0.20
2024-01-19,West,Widget C,470.00,2,28,Startup,0.00
```

- [ ] **Step 2: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests pass with no failures.

- [ ] **Step 3: Smoke test — profiler on sample.csv**

Run:
```bash
python .analytics/tools/profiler.py raw/sample.csv --output-dir output
```
Expected: JSON printed to stdout, `output/profile.json` created. Verify it contains `shape`, `columns` with `sales`, `region`, `customer_age` etc.

- [ ] **Step 4: Smoke test — cleaner on sample.csv**

Run:
```bash
python .analytics/tools/cleaner.py raw/sample.csv --output-dir output
```
Expected: JSON log showing `null_imputation` for `customer_age` (3 nulls), `output/cleaned.csv` created.

- [ ] **Step 5: Smoke test — viz on sample.csv**

Run:
```bash
python .analytics/tools/viz.py raw/sample.csv --type bar --x region --y sales --title "Sales by Region" --format html --output-dir output/charts
```
Expected: Path to `.html` file printed, file exists in `output/charts/`, file is >0 bytes.

- [ ] **Step 6: Smoke test — report**

Run:
```bash
python .analytics/tools/report.py --profile output/profile.json --dataset-name "sample" --insights "Sales are highest in the North" "3 nulls in customer_age" --output-dir output/reports
```
Expected: Path to `output/reports/report-YYYY-MM-DD.html` printed, file is valid HTML.

- [ ] **Step 7: Final commit**

```bash
git add raw/sample.csv
git commit -m "feat: add sample.csv for smoke testing the analytics pipeline"
```

---

## Self-Review Checklist

- [x] **Spec coverage:** profiler ✓, cleaner ✓, viz ✓, report ✓, feedback ✓, agents ✓, skills ✓, PostToolUse hook ✓, sample data ✓, AnalyticsContext (handled in viz-recommender agent via open-ended mode) ✓
- [x] **No placeholders:** All code blocks are complete and runnable
- [x] **Type consistency:** `load_dataframe` used in tasks 3–6 matches the signature defined in task 2; `profile_dataframe` return shape used in task 6 matches task 3 output; `clean_dataframe` return tuple used consistently
- [x] **TDD enforced:** Every tool has failing tests written before implementation
