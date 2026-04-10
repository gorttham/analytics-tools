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
