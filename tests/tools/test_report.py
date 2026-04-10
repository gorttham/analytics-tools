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
