# Sheet Doctor

Sheet Doctor is an open-source Python-based Excel profiling and data quality assessment tool designed for analysts, BI developers, data engineers, and business users.

The tool analyzes Excel workbooks and generates BI-ready profiling reports that help users quickly understand data structure, identify quality issues, identify potentially sensitive data, and prepare datasets for reporting and analytics.

---

# Features

## Workbook Analysis

* Multi-sheet workbook support
* Sheet enumeration
* Row count
* Column count
* Workbook summary

## Data Profiling

For each column:

* Data type detection
* Missing value count
* Missing percentage
* Unique value count

### Numeric Columns

* Minimum value
* Maximum value
* Mean value

### Text Columns

* Top 5 most frequent values

---

## Data Quality Checks

* Duplicate row detection
* Blank column detection
* High missing-value detection
* Numeric values stored as text

---

## PII Detection (New)

Sheet Doctor can identify columns that may contain Personally Identifiable Information (PII).

### Supported PII Types

* First Name
* Last Name
* Full Name
* Address
* Email Address
* Phone Number
* Social Security Number (SSN)
* Credit Card Number
* Date of Birth
* Passport Number
* Driver License Number
* Bank Account Number

### Detection Methods

#### Column Name Detection

Sheet Doctor compares column names against a configurable PII dictionary.

Examples:

* FirstName
* first_name
* Last Name
* Email
* email_address
* Phone
* Mobile
* SSN
* CardNumber

#### Pattern-Based Detection

Sheet Doctor can also inspect sample values and identify common patterns such as:

* Email addresses
* Phone numbers
* SSNs
* Credit card-like numbers

For privacy and security reasons, actual values are never displayed in reports.

Only metadata is reported.

---

## PII Detection Summary

A dedicated section is added to the HTML report.

Example:

| Sheet     | Column | PII Type               | Detection Method |
| --------- | ------ | ---------------------- | ---------------- |
| Customers | Email  | Email Address          | Column Name      |
| Customers | Phone  | Phone Number           | Pattern Match    |
| Employees | SSN    | Social Security Number | Column Name      |

---

## Sensitive Data Warning

If PII is detected, the report displays a warning banner.

Example:

> Warning: This workbook may contain personally identifiable information. Be careful when sharing this file with others or uploading it to AI tools.

If no PII is detected:

> No obvious PII columns were detected based on configured rules.

---

# Installation

```bash
pip install -r requirements.txt
```

---

# Usage

Analyze a workbook:

```bash
sheet-doctor scan workbook.xlsx
```

Generate an HTML profiling report:

```bash
sheet-doctor scan workbook.xlsx --output report.html
```

---

# Example Report Sections

The generated report may contain:

* Workbook Summary
* Sheet Statistics
* Column Profiles
* Data Quality Findings
* Duplicate Analysis
* Missing Data Analysis
* PII Detection Summary

---

# PII Dictionary

PII identification rules are maintained in:

```text
pii_columns.md
```

The dictionary can be extended to support additional organization-specific fields.

Example entries:

```markdown
## Email

- email
- email_address
- emailid

## Phone Number

- phone
- phone_number
- mobile
- mobile_number

## SSN

- ssn
- social_security_number
```

---

# Limitations

PII detection is heuristic-based and should not be considered a compliance or legal certification.

False positives and false negatives may occur.

Users should always manually review sensitive workbooks before:

* Sharing with external parties
* Uploading to AI systems
* Publishing datasets
* Distributing reports

---

# Supported Formats

* XLSX
* XLS

---

# Roadmap

## Version 1.1

* Data Quality Score
* Excel Export
* Schema Comparison

## Version 1.2

* AI Insights
* Anomaly Detection
* Executive Workbook Summaries

## Version 2.0

* Enhanced PII Detection
* Data Classification
* Compliance Readiness Checks
* AI-generated Data Dictionaries
* Data Governance Insights

---

# Contributing

Contributions are welcome.

Potential areas:

* Additional PII patterns
* Industry-specific classifications
* Performance improvements
* New report visualizations
* Additional file formats

---

# Security Notice

Sheet Doctor helps identify potentially sensitive information but does not guarantee complete detection of all PII, confidential, regulated, or protected data.

Always apply appropriate security, privacy, and governance controls when handling spreadsheets containing sensitive information.

---

# License

Open Source.
See the project's LICENSE file for details.
