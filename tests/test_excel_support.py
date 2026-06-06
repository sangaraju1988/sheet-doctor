import struct
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
from typer.testing import CliRunner

from sheet_doctor.cli import app
from sheet_doctor.profiler import profile_workbook


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
