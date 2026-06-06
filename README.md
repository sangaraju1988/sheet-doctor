# Sheet Doctor

A lightweight Python CLI tool that profiles Excel workbooks and generates data quality reports.
Sheet Doctor supports modern `.xlsx` workbooks and legacy `.xls` workbooks.

## Features

### Workbook Analysis

* Multi-sheet workbook support
* Row and column counts
* Sheet-level statistics
* Workbook overview summary

### Data Profiling

* Automatic data type detection
* Missing value analysis
* Unique value counts
* Numeric column statistics

  * Minimum
  * Maximum
  * Average
* Text column profiling

  * Top 5 most frequent values

### Data Quality Checks

* Duplicate row detection
* Blank column detection
* High missing-value identification
* Numeric values stored as text detection

### Reporting

* HTML report generation
* Easy-to-read summary tables
* BI-ready workbook assessment

---

## Installation

Clone the repository:

```bash
git clone https://github.com/sangaraju1988/sheet-doctor.git
cd sheet-doctor
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run Sheet Doctor against an Excel workbook:

```bash
python -m sheet_doctor.cli Financial_Sample.xlsx report.html
```

Legacy `.xls` workbooks are supported as well:

```bash
python -m sheet_doctor.cli legacy_sales.xls legacy_report.html
```

More examples:

```bash
python -m sheet_doctor.cli sales.xlsx report.html
python -m sheet_doctor.cli legacy_sales.xls report.html
```

### Parameters

| Parameter             | Description          |
| --------------------- | -------------------- |
| Financial_Sample.xlsx | Input Excel workbook (`.xlsx` or `.xls`) |
| report.html           | Output report file   |

---

## Example Output

Sheet Doctor generates a report containing:

```text
Workbook Summary
├── Sheet Overview
├── Row & Column Counts

Data Quality Issues
├── Missing Values
├── Duplicate Rows
├── Blank Columns
├── Data Type Warnings

Column Profiles
├── Numeric Statistics
├── Text Frequencies
├── Unique Counts

HTML Report
```

---

## Project Structure

```text
sheet-doctor/
│
├── sheet_doctor/
│   ├── __init__.py
│   ├── cli.py
│   ├── profiler.py
│   └── report.py
│
├── templates/
│   └── report.html
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Roadmap

### Version 1.0

* [x] Excel workbook profiling
* [x] Data quality checks
* [x] HTML report generation

### Version 1.1

* [ ] Data quality scoring
* [ ] Export report to Excel
* [ ] Schema comparison between workbooks

### Version 1.2

* [ ] AI-generated workbook insights
* [ ] Automatic anomaly detection
* [ ] Natural language summary generation

### Version 2.0

* [ ] PII detection
* [ ] Data governance checks
* [ ] AI-powered data documentation
* [ ] Dashboard readiness scoring

---

## Contributing

Contributions, feature requests, and bug reports are welcome.

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## License

MIT
