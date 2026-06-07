import struct
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
from typer.testing import CliRunner

from sheet_doctor.cli import app
from sheet_doctor.profiler import profile_workbook
from sheet_doctor.report import generate_report


runner = CliRunner()


def _record(opcode: int, data: bytes = b"") -> bytes:
    return struct.pack("<HH", opcode, len(data)) + data


def _write_minimal_xls(path: Path) -> None:
    cell_attr = b"\0\0\0"
    content = _record(0x0009, struct.pack("<HH", 0x0007, 0x0010))
    content += _record(0x0042, struct.pack("<H", 1252))
    content += _record(0x0000, struct.pack("<HHHH", 0, 2, 0, 2))
    content += _record(0x0004, struct.pack("<HH", 0, 0) + cell_attr + b"\x04name")
    content += _record(0x0004, struct.pack("<HH", 0, 1) + cell_attr + b"\x05value")
    content += _record(0x0002, struct.pack("<HH", 1, 0) + cell_attr + struct.pack("<H", 1))
    content += _record(0x0002, struct.pack("<HH", 1, 1) + cell_attr + struct.pack("<H", 10))
    content += _record(0x000A)
    path.write_bytes(content)


class ExcelSupportTests(unittest.TestCase):
    def test_profiles_valid_xlsx_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            workbook = Path(tmpdir) / "sales.xlsx"
            pd.DataFrame({"name": ["north", "south"], "value": [10, 20]}).to_excel(
                workbook,
                index=False,
                engine="openpyxl",
            )

            profile = profile_workbook(workbook)

        self.assertEqual(profile["sheet_count"], 1)
        self.assertEqual(profile["sheets"][0]["row_count"], 2)
        self.assertEqual(profile["sheets"][0]["column_count"], 2)

    def test_detects_pii_from_column_name_dictionary(self) -> None:
        with TemporaryDirectory() as tmpdir:
            workbook = Path(tmpdir) / "customers.xlsx"
            pd.DataFrame(
                {
                    "First Name": ["Ada", "Grace"],
                    "phone_number": ["555-123-4567", "555-987-6543"],
                    "order_total": [10, 20],
                }
            ).to_excel(workbook, index=False, engine="openpyxl")

            profile = profile_workbook(workbook)

        pii_columns = profile["sheets"][0]["pii_columns"]
        self.assertEqual(
            {(item["column"], item["pii_type"], item["detection_method"]) for item in pii_columns},
            {
                ("First Name", "First Name", "column name match"),
                ("phone_number", "Phone Number", "column name match"),
            },
        )

    def test_detects_pii_from_value_patterns_without_storing_values(self) -> None:
        with TemporaryDirectory() as tmpdir:
            workbook = Path(tmpdir) / "contacts.xlsx"
            pd.DataFrame(
                {
                    "contact": ["ada@example.com", "grace@example.com"],
                    "notes": ["ok", "ok"],
                }
            ).to_excel(workbook, index=False, engine="openpyxl")

            profile = profile_workbook(workbook)

        pii_columns = profile["sheets"][0]["pii_columns"]
        self.assertEqual(len(pii_columns), 1)
        self.assertEqual(pii_columns[0]["column"], "contact")
        self.assertEqual(pii_columns[0]["pii_type"], "Email")
        self.assertEqual(pii_columns[0]["detection_method"], "value pattern match")
        self.assertNotIn("ada@example.com", str(profile))

    def test_report_includes_pii_warning_and_summary(self) -> None:
        profile = {
            "file": "customers.xlsx",
            "sheet_count": 1,
            "sheets": [
                {
                    "name": "Customers",
                    "row_count": 2,
                    "column_count": 1,
                    "missing_values": 0,
                    "duplicate_rows": 0,
                    "columns": [],
                    "pii_columns": [
                        {
                            "sheet": "Customers",
                            "column": "email",
                            "pii_type": "Email",
                            "detection_method": "column name match",
                            "reason": "Column name matched configured pattern 'email'",
                        }
                    ],
                }
            ],
        }

        with TemporaryDirectory() as tmpdir:
            report = Path(tmpdir) / "report.html"
            generate_report(profile, report)
            html = report.read_text(encoding="utf-8")

        self.assertIn("PII Detection Summary", html)
        self.assertIn("Warning: This workbook may contain personally identifiable information.", html)
        self.assertIn("Customers", html)
        self.assertIn("email", html)
        self.assertIn("column name match", html)

    def test_report_includes_no_pii_message(self) -> None:
        profile = {
            "file": "sales.xlsx",
            "sheet_count": 1,
            "sheets": [
                {
                    "name": "Sales",
                    "row_count": 1,
                    "column_count": 1,
                    "missing_values": 0,
                    "duplicate_rows": 0,
                    "columns": [],
                    "pii_columns": [],
                }
            ],
        }

        with TemporaryDirectory() as tmpdir:
            report = Path(tmpdir) / "report.html"
            generate_report(profile, report)
            html = report.read_text(encoding="utf-8")

        self.assertIn("No obvious PII columns were detected based on configured rules.", html)

    def test_profiles_valid_xls_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            workbook = Path(tmpdir) / "legacy_sales.xls"
            _write_minimal_xls(workbook)

            profile = profile_workbook(workbook)

        self.assertEqual(profile["sheet_count"], 1)
        self.assertEqual(profile["sheets"][0]["row_count"], 1)
        self.assertEqual(profile["sheets"][0]["column_count"], 2)

    def test_cli_rejects_unsupported_file_type(self) -> None:
        with TemporaryDirectory() as tmpdir:
            workbook = Path(tmpdir) / "sales.csv"
            workbook.write_text("name,value\nnorth,10\n", encoding="utf-8")
            report = Path(tmpdir) / "report.html"

            result = runner.invoke(app, [str(workbook), str(report)])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("Unsupported file type", result.output)
        self.assertIn(".xls, .xlsx", result.output)

    def test_cli_rejects_missing_file(self) -> None:
        with TemporaryDirectory() as tmpdir:
            workbook = Path(tmpdir) / "missing.xlsx"
            report = Path(tmpdir) / "report.html"

            result = runner.invoke(app, [str(workbook), str(report)])

        self.assertEqual(result.exit_code, 1)
        self.assertIn("File not found", result.output)


if __name__ == "__main__":
    unittest.main()
