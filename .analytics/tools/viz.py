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
