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
    # median of all-null series is NaN — no valid fill value, column stays null
    assert cleaned["a"].isna().all()


def test_log_includes_final_shape(dirty_df):
    _, log = clean_dataframe(dirty_df)
    assert "final_shape" in log
    assert "rows" in log["final_shape"]


def test_invalid_input():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        clean_dataframe([1, 2, 3])
