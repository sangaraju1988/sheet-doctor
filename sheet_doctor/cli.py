from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from sheet_doctor import profiler, report


app = typer.Typer(help="Scan Excel files and generate Sheet Doctor reports.")
console = Console()


def _validate_excel_path(excel_path: Path) -> None:
    supported = ", ".join(sorted(profiler.SUPPORTED_EXCEL_ENGINES))

    if not excel_path.exists():
        console.print(f"[red]File not found:[/] {excel_path}")
        raise typer.Exit(code=1)

    if not excel_path.is_file():
        console.print(f"[red]Not a file:[/] {excel_path}")
        raise typer.Exit(code=1)

    if excel_path.suffix.lower() not in profiler.SUPPORTED_EXCEL_ENGINES:
        console.print(
            f"[red]Unsupported file type:[/] {excel_path.suffix or '<none>'}. "
            f"Supported formats: {supported}."
        )
        raise typer.Exit(code=1)


def _require_callable(module: Any, name: str) -> Any:
    func = getattr(module, name, None)
    if not callable(func):
        console.print(f"[red]Missing required function:[/] {module.__name__}.{name}")
        raise typer.Exit(code=1)
    return func


@app.command()
def scan(
    excel_path: Path = typer.Argument(
        ...,
        help="Path to the Excel file to scan.",
    ),
    report_path: Path = typer.Argument(
        ...,
        help="Path where the generated report should be written.",
    ),
) -> None:
    """Scan an Excel workbook and write an HTML report."""
    _validate_excel_path(excel_path)

    profile_workbook = _require_callable(profiler, "profile_workbook")
    generate_report = _require_callable(report, "generate_report")

    console.print(f"[cyan]Scanning:[/] {excel_path}")
    try:
        profile = profile_workbook(excel_path)
    except profiler.UnsupportedExcelFormatError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc
    except profiler.MissingExcelDependencyError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc
    except profiler.ExcelReadError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(code=1) from exc

    console.print(f"[cyan]Writing report:[/] {report_path}")
    generate_report(profile, report_path)

    console.print(f"[green]Report created:[/] {report_path}")


if __name__ == "__main__":
    app()
