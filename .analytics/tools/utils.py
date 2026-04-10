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
