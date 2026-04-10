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
