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
