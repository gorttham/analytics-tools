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
