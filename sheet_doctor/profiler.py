import re
from pathlib import Path
from typing import Any
from zipfile import BadZipFile

import pandas as pd


PII_DICTIONARY_PATH = Path(__file__).resolve().parent.parent / "pii_columns.md"
SUPPORTED_EXCEL_ENGINES = {
    ".xlsx": "openpyxl",
    ".xls": "xlrd",
}

GENERIC_PII_PATTERNS = {"name", "cell", "passport", "address", "phone", "mobile", "email", "ssn", "dob"}
VALUE_SAMPLE_SIZE = 100
VALUE_PATTERN_MIN_MATCHES = 2
VALUE_PATTERN_MIN_RATIO = 0.6
EMAIL_RE = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
PHONE_RE = re.compile(r"^\+?[\d\s().-]{7,}$")
SSN_RE = re.compile(r"^\d{3}-\d{2}-\d{4}$")


class UnsupportedExcelFormatError(ValueError):
    """Raised when a workbook path has an unsupported extension."""


class MissingExcelDependencyError(RuntimeError):
    """Raised when the Excel reader dependency for a format is unavailable."""


class ExcelReadError(RuntimeError):
    """Raised when a workbook cannot be read as a valid Excel file."""


def _normalize_pii_pattern(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def load_pii_dictionary(dictionary_path: str | Path = PII_DICTIONARY_PATH) -> list[dict[str, Any]]:
    """Load PII column-name rules from a small Markdown dictionary."""
    path = Path(dictionary_path)
    rules: list[dict[str, Any]] = []
    current_type = ""

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current_type = stripped.removeprefix("## ").strip()
            rules.append({"pii_type": current_type, "patterns": []})
        elif current_type and stripped.startswith("- "):
            pattern = stripped.removeprefix("- ").strip()
            rules[-1]["patterns"].append(
                {
                    "raw": pattern,
                    "normalized": _normalize_pii_pattern(pattern),
                }
            )

    return rules


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


def _match_column_name(column_name: Any, pii_rules: list[dict[str, Any]]) -> dict[str, str] | None:
    column_normalized = _normalize_pii_pattern(column_name)

    for rule in pii_rules:
        for pattern in rule["patterns"]:
            pattern_normalized = pattern["normalized"]
            if not pattern_normalized:
                continue
            exact_match = column_normalized == pattern_normalized
            specific_contains_match = (
                pattern_normalized not in GENERIC_PII_PATTERNS
                and pattern_normalized in column_normalized
            )
            if exact_match or specific_contains_match:
                return {
                    "pii_type": rule["pii_type"],
                    "detection_method": "column name match",
                    "reason": f"Column name matched configured pattern '{pattern['raw']}'",
                }

    return None


def _is_phone_like(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return bool(PHONE_RE.match(value)) and 10 <= len(digits) <= 15


def _is_luhn_valid(number: str) -> bool:
    digits = [int(char) for char in number if char.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False

    checksum = 0
    parity = len(digits) % 2
    for index, digit in enumerate(digits):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    return checksum % 10 == 0


def _value_pattern_match(series: pd.Series) -> dict[str, str] | None:
    non_missing = series.dropna().head(VALUE_SAMPLE_SIZE)
    values = [str(value).strip() for value in non_missing if str(value).strip()]
    if not values:
        return None

    checks = [
        ("Email", lambda value: bool(EMAIL_RE.match(value))),
        ("SSN", lambda value: bool(SSN_RE.match(value))),
        ("Credit Card Number", _is_luhn_valid),
        ("Phone Number", _is_phone_like),
    ]

    for pii_type, matcher in checks:
        match_count = sum(1 for value in values if matcher(value))
        required_matches = min(VALUE_PATTERN_MIN_MATCHES, len(values))
        if match_count >= required_matches and match_count / len(values) >= VALUE_PATTERN_MIN_RATIO:
            return {
                "pii_type": pii_type,
                "detection_method": "value pattern match",
                "reason": f"{match_count} sampled non-empty values matched {pii_type.lower()} pattern",
            }

    return None


def _detect_pii_columns(df: pd.DataFrame, sheet_name: str, pii_rules: list[dict[str, Any]]) -> list[dict[str, str]]:
    detections = []

    for column in df.columns:
        detection = _match_column_name(column, pii_rules) or _value_pattern_match(df[column])
        if detection:
            detections.append(
                {
                    "sheet": sheet_name,
                    "column": str(column),
                    **detection,
                }
            )

    return detections


def profile_workbook(excel_path: str | Path) -> dict[str, Any]:
    """Read an Excel workbook and return profile data for every sheet."""
    workbook_path = Path(excel_path)
    engine = get_excel_engine(workbook_path)
    pii_rules = load_pii_dictionary()

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
                "pii_columns": _detect_pii_columns(df, sheet_name, pii_rules),
            }
            for sheet_name, df in sheets.items()
        ],
    }
