# Sheet Doctor

A lightweight Python CLI tool that profiles Excel workbooks and generates data quality reports.

## Features

- Workbook overview
- Sheet statistics
- Missing value analysis
- Duplicate row detection
- Data type profiling
- Numeric column summaries
- Text column frequency analysis
- HTML report generation

## Installation

```bash
git clone https://github.com/sangaraju1988/excel-inspector.git
cd excel-inspector

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

```bash
python -m sheet_doctor.cli Financial_Sample.xlsx report.html
```

## Example Output

The tool generates:

```text
Workbook Summary
Data Quality Issues
Column Profiles
HTML Report
```

## Project Structure

```text
excel-inspector/
│
├── sheet_doctor/
│   ├── cli.py
│   ├── profiler.py
│   ├── report.py
│   └── __init__.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Roadmap

- [ ] AI-generated insights
- [ ] PII detection
- [ ] Data quality scoring
- [ ] Schema comparison
- [ ] Excel-to-HTML dashboard export

## License

MIT
