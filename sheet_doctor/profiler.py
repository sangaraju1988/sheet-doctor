from pathlib import Path
from typing import Any
from zipfile import BadZipFile

import pandas as pd


SUPPORTED_EXCEL_ENGINES = {
    ".xlsx": "openpyxl",
    ".xls": "xlrd",
}


class UnsupportedExcelFormatError(ValueError):
    """Raised when a workbook path has an unsupported extension."""


class MissingExcelDependencyError(RuntimeError):
    """Raised when the Excel reader dependency for a format is unavailable."""


class ExcelReadError(RuntimeError):
    """Raised when a workbook cannot be read as a valid Excel file."""


def get_excel_engine(excel_path: str | Path) -> str:
    """Return the pandas reader engine for a supported Excel workbook."""
    suffix = Path(excel_path).suffix.lower()
    try:
        return SUPPORTED_EXCEL_ENGINES[suffix]
    except KeyError as exc:
        supported = ", ".join(sorted(SUPPORTED_EXCEL_ENGINES))
        raise UnsupportedExcelFormatError(
            f"Unsupported Excel format '{suffix or '<none>'}'. "
            f"Supported formats: {supported}."
        ) from exc


def _profile_column(series: pd.Series) -> dict[str, Any]:
    missing_count = int(series.isna().sum())
    non_missing = series.dropna()

    return {
        "name": str(series.name),
        "dtype": str(series.dtype),
        "missing_values": missing_count,
        "missing_percent": float(missing_count / len(series) * 100) if len(series) else 0.0,
        "unique_values": int(non_missing.nunique()),
    }


def profile_workbook(excel_path: str | Path) -> dict[str, Any]:
    """Read an Excel workbook and return profile data for every sheet."""
    workbook_path = Path(excel_path)
    engine = get_excel_engine(workbook_path)

    try:
        sheets = pd.read_excel(workbook_path, sheet_name=None, engine=engine)
    except (ImportError, ModuleNotFoundError) as exc:
        raise MissingExcelDependencyError(
            f"Missing dependency for {workbook_path.suffix.lower()} files. "
            f"Install the '{engine}' package and try again."
        ) from exc
    except (BadZipFile, ValueError) as exc:
        raise ExcelReadError(
            f"Could not read '{workbook_path}'. The file may be corrupt or "
            "not a valid Excel workbook."
        ) from exc
    except Exception as exc:
        if exc.__class__.__module__.startswith("xlrd"):
            raise ExcelReadError(
                f"Could not read '{workbook_path}'. The file may be corrupt or "
                "not a valid Excel workbook."
            ) from exc
        raise

    return {
        "file": str(workbook_path),
        "sheet_count": len(sheets),
        "sheets": [
            {
                "name": sheet_name,
                "row_count": int(df.shape[0]),
                "column_count": int(df.shape[1]),
                "missing_values": int(df.isna().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
                "columns": [_profile_column(df[column]) for column in df.columns],
            }
            for sheet_name, df in sheets.items()
        ],
    }
