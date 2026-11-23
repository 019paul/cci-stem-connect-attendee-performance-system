
# CCI STEM Connect
## Attendee Performance Evaluation System

**Organisation:** CCI STEM Connect
**Project:** Attendee Performance Evaluation Model
**System Type:** Rule-Based Performance Evaluation and Reporting System
**Version:** 1.0.0
**Status:** Core functionality implemented and tested

---

## 1. Project Overview

The CCI STEM Connect Attendee Performance Evaluation System is a Python-based application developed to evaluate, measure, rank, and report the performance of participants involved in CCI STEM Connect programmes and activities.

The system uses a weighted scoring methodology to assess attendees based on attendance, session participation, practical engagement, teamwork, activities completed, and feedback scores.

It processes attendee records, validates input data, calculates performance scores, assigns performance categories, ranks attendees, and generates structured reports.

A Streamlit dashboard provides a visual interface for reviewing performance results and event statistics.

## 2. Project Objectives

The objectives of the system are to:

- Evaluate attendee performance using defined assessment criteria.
- Provide a consistent and transparent scoring methodology.
- Identify high-performing attendees.
- Highlight areas where attendees may require improvement.
- Generate individual and overall performance reports.
- Present performance results through an interactive dashboard.
- Support data-informed programme evaluation and decision-making.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data processing and analysis |
| Streamlit | Interactive dashboard |
| CSV | Data storage and report exports |
| PowerShell | Running and managing the application |
| Visual Studio Code | Development environment |

## 4. Project Structure

```text
CCI_STEM_Connect_Model/
│
├── sample_data/
│   └── cci_attendees_sample.csv
├── src/
│   ├── performance_model.py
│   └── test_validation.py
│
├── app.py
├── .gitignore
├── requirements.txt
└── README.md
```

The tracked sample dataset contains fictional demonstration records. The
private `data/` and generated `outputs/` folders are excluded from Git so
company attendee records and performance reports are not published.

## 5. Assessment Criteria

The system evaluates attendees using six assessment criteria.

| Assessment criterion | Weight |
|---|---:|
| Attendance rate | 20% |
| Session participation | 15% |
| Practical engagement | 20% |
| Teamwork | 15% |
| Activities completed | 20% |
| Feedback score | 10% |
| **Total** | **100%** |

## 6. Performance Scoring Methodology

The system uses a weighted scoring formula:

P = (0.20 × A) + (0.15 × S) + (0.20 × E) + (0.15 × T) + (0.20 × C) + (0.10 × F)

Where:

- P = Overall performance score
- A = Attendance rate
- S = Session participation percentage
- E = Practical engagement percentage
- T = Teamwork percentage
- C = Activities completed percentage
- F = Feedback score percentage

Scores recorded on a scale of 0–10 are converted into percentages before calculation.

The resulting performance score is expressed on a scale of 0–100.

## 7. Performance Classification

The system assigns performance categories using the following thresholds:

| Score range | Performance category |
|---|---|
| 90–100 | Outstanding |
| 75–89.99 | Excellent |
| 60–74.99 | Good |
| 40–59.99 | Average |
| Below 40 | Needs Improvement |

## 8. Data Validation

Before performance evaluation, the system validates attendee records.

Validation checks include:

- Required columns must be present.
- Attendee records must not be empty.
- Attendee IDs must be unique.
- Attendee names must not be blank.
- Categories must be Student, Mentor, or Facilitator.
- Numeric fields must contain valid numbers.
- Attendance must be between 0 and 100.
- Participation, engagement, teamwork, and feedback scores must be between 0 and 10.
- Activities completed must be between 0 and 100.

Invalid records are rejected with descriptive error messages.

## 9. System Outputs

The application generates three CSV reports.

### Attendee Performance Report

Contains individual attendee results, including:

- Attendee ID
- Attendee name
- Category
- Performance score
- Performance category
- Ranking

### Event Summary Report

Provides overall event statistics, including:

- Total attendees
- Average performance score
- Highest performance score
- Lowest performance score
- Top-performing attendee
- Lowest-performing attendee

### Performance Distribution Report

Shows the number of attendees in each performance category.

## 10. Dashboard

The Streamlit dashboard provides a visual presentation of attendee performance results.

It allows users to review overall event statistics, attendee rankings, performance categories, and evaluation results.

## 11. Testing and Quality Assurance

The data validation testing script contains ten test scenarios.

The completed tests cover:

1. Valid attendee record.
2. Missing attendee name.
3. Duplicate attendee ID.
4. Invalid attendee category.
5. Attendance rate above 100.
6. Session participation above 10.
7. Non-numeric feedback score.
8. Missing required column.
9. Lowercase category normalization.
10. Empty dataset.

**Recorded test result:**

- Total tests: 10
- Passed: 10
- Failed: 0

The three exported reports were checked, and the dashboard was confirmed to display consistent results.

## 12. Installation and Execution

### Prerequisites

- Python installed.
- Visual Studio Code or another Python development environment.
- Required Python packages.

### Install dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

### Run the performance evaluation model

```powershell
python .\src\performance_model.py
```

### Run the validation tests

```powershell
python .\src\test_validation.py
```

### Launch the dashboard

```powershell
python -m streamlit run app.py
```

The dashboard will open in your default web browser.

## 13. Current Limitations

- The system currently uses CSV files as its data source.
- The application is designed around a single event dataset.
- The scoring weights and classification thresholds require organisational approval before official operational use.
- Role-specific scoring adjustments are not currently implemented.
- User authentication and role-based access control are not yet implemented.
- The system does not currently provide a centralised multi-user database.

## 14. Future Improvements

Potential future improvements include:

- Integration with a centralised database.
- Secure user authentication and access control.
- Historical performance tracking across multiple events.
- Automated report generation in PDF and Excel formats.
- Additional dashboard filters and visual analytics.
- Role-specific assessment criteria where approved.
- Deployment to a secure hosting environment.

## 15. Organisation

**CCI STEM Connect**

This system is intended to support the evaluation, monitoring, and reporting of attendee performance across CCI STEM Connect programmes and activities.

---

**Project documentation maintained by the CCI STEM Connect development team.**
