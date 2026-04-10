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
