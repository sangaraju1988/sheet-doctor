# Sheet Doctor

**Sheet Doctor** is an open-source Python CLI tool that analyzes Excel workbooks and generates BI-ready data quality reports.

Designed for analysts, BI developers, and data engineers, Sheet Doctor helps you quickly understand workbook structure, identify data quality issues, and prepare datasets for reporting and analytics.

---

## Features

### Workbook Analysis

* Multi-sheet workbook support
* Workbook overview and statistics
* Row and column counts
* Sheet-level summaries

### Data Profiling

* Automatic data type detection
* Missing value analysis
* Unique value counts
* Numeric column statistics

  * Minimum
  * Maximum
  * Mean
* Text column analysis

  * Most frequent values
  * Cardinality checks

### Data Quality Checks

* Duplicate row detection
* Empty column detection
* High missing-value identification
* Numeric values stored as text detection
* Basic data consistency checks

### Reporting

* HTML report generation
* Workbook summary dashboard
* Data quality findings
* Column-level profiling

---

## Installation

Clone the repository:

```bash
git clone https://github.com/sangaraju1988/sheet-doctor.git
cd sheet-doctor
```

Create and activate a virtual environment:

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Generate a report from an Excel workbook:

```bash
python -m sheet_doctor.cli Financial_Sample.xlsx report.html
```

### Arguments

| Argument              | Description          |
| --------------------- | -------------------- |
| Financial_Sample.xlsx | Input Excel workbook |
| report.html           | Output HTML report   |

---

## Example Output

Sheet Doctor generates reports containing:

```text
Workbook Summary
├── Sheet Overview
├── Row Count
├── Column Count

Data Quality Checks
├── Missing Values
├── Duplicate Rows
├── Empty Columns
├── Data Type Warnings

Column Profiles
├── Numeric Statistics
├── Text Analysis
├── Unique Counts

Generated HTML Report
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
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Roadmap

### Version 1.0

* [x] Excel workbook profiling
* [x] Data quality analysis
* [x] HTML report generation

### Version 1.1

* [ ] Data quality score
* [ ] Excel export reports
* [ ] Workbook comparison

### Version 1.2

* [ ] AI-generated workbook insights
* [ ] Automated anomaly detection
* [ ] Natural language summaries

### Version 2.0

* [ ] PII detection
* [ ] Data governance checks
* [ ] AI-powered data documentation
* [ ] Dashboard readiness assessment

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## License

MIT License
