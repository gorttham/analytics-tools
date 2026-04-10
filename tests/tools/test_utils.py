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
