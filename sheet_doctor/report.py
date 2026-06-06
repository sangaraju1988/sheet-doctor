from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _quality_issues(profile: dict[str, Any]) -> list[dict[str, Any]]:
    issues = []

    for sheet in profile.get("sheets", []):
        missing_values = sheet.get("missing_values", 0)
        duplicate_rows = sheet.get("duplicate_rows", 0)

        if missing_values:
            issues.append(
                {
                    "sheet": sheet.get("name", ""),
                    "issue": "Missing values",
                    "count": missing_values,
                }
            )

        if duplicate_rows:
            issues.append(
                {
                    "sheet": sheet.get("name", ""),
                    "issue": "Duplicate rows",
                    "count": duplicate_rows,
                }
            )

    return issues


def generate_report(profile: dict[str, Any], report_path: str | Path) -> None:
    """Generate an HTML workbook profile report."""
    output_path = Path(report_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    environment = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = environment.get_template("report.html")

    html = template.render(
        profile=profile,
        quality_issues=_quality_issues(profile),
    )
    output_path.write_text(html, encoding="utf-8")
