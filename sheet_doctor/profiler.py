from pathlib import Path
from typing import Any

import pandas as pd


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
    sheets = pd.read_excel(workbook_path, sheet_name=None)

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
