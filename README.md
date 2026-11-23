# CCI STEM Connect – Attendee Performance Evaluation System

A data-driven dashboard for evaluating attendee attendance, participation, practical engagement, teamwork, activity completion, and feedback during CCI STEM Connect programmes.

## Project Overview

The **CCI STEM Connect Attendee Performance Evaluation System** is a Python-based application designed to support the evaluation and monitoring of programme attendees.

The system provides an interactive dashboard where programme performance data can be explored, individual attendee performance can be reviewed, and summary reports can be generated.

It helps programme organisers understand attendee engagement, identify performance patterns, and make more informed decisions when evaluating programme outcomes.

## Key Features

- **Performance Dashboard:** View programme-wide performance summaries and key indicators.
- **Attendance Monitoring:** Review attendee attendance rates and attendance patterns.
- **Attendee Performance:** Search, filter, and compare attendee performance records.
- **Individual Profiles:** View detailed performance information for individual attendees.
- **Performance Analytics:** Explore performance distributions, category comparisons, and engagement patterns.
- **Programme Insights:** Review attendance, practical engagement, teamwork, and other programme indicators.
- **Reports and Downloads:** Export performance records and summary reports in CSV and Excel formats.
- **Data Management:** Upload supported CSV or Excel datasets and restore the original dataset.
- **Data Validation:** Check uploaded data against the required structure before evaluation.

## Performance Evaluation

The system evaluates attendees using six performance indicators:

| Indicator | Weight |
|---|---:|
| Attendance Rate | 20% |
| Session Participation | 15% |
| Practical Engagement | 20% |
| Teamwork | 15% |
| Activities Completed | 20% |
| Feedback Score | 10% |
| **Total** | **100%** |

### Performance Classification

Attendees are classified according to their overall performance scores.

| Score | Classification |
|---|---|
| 90–100 | Outstanding |
| 75–89.99 | Excellent |
| 60–74.99 | Good |
| 40–59.99 | Average |
| Below 40 | Needs Improvement |

## Technologies Used

- **Python** – Core application logic and data processing.
- **Streamlit** – Interactive web dashboard.
- **Pandas** – Data manipulation and analysis.
- **Scikit-learn** – Machine-learning tools and supporting analysis modules.
- **OpenPyXL** – Excel file handling and report generation.
- **Git and GitHub** – Version control and project management.

## Project Structure

```text
CCI_STEM_Connect_Model/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── cci_attendees.csv
│
├── sample_data/
│   └── cci_attendees_sample.csv
│
├── outputs/
│
└── src/
    ├── performance_model.py
    ├── test_validation.py
    │
    └── ml/
        ├── __init__.py
        ├── clustering.py
        ├── data_preparation.py
        ├── model_evaluation.py
        └── random_forest.py
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/019paul/cci-stem-connect-attendee-performance-system.git
```

### 2. Navigate to the Project Directory

```bash
cd CCI_STEM_Connect_Model
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python -m streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your web browser to access the dashboard.

## Dataset Requirements

The application expects attendee records containing the following fields:

| Column | Description |
|---|---|
| `attendee_id` | Unique attendee identifier |
| `attendee_name` | Attendee's name |
| `category` | Attendee category |
| `attendance_rate` | Attendance percentage |
| `session_participation` | Session participation score |
| `practical_engagement` | Practical engagement score |
| `teamwork` | Teamwork score |
| `activities_completed` | Activities completed percentage |
| `feedback_score` | Feedback score |

The sample dataset in `sample_data/` contains fictional records for testing.

## Data Privacy

Attendee information may contain confidential programme records.

The original dataset and generated output files are excluded from version control through `.gitignore`. Only approved sample data should be committed to the public or shared repository.

Users should ensure that uploaded datasets are authorised for processing and that sensitive attendee information is handled appropriately.

## Project Purpose

The purpose of this project is to provide a structured and accessible approach to attendee performance evaluation, helping programme organisers monitor engagement, assess outcomes, and support evidence-based programme improvement.

## Author

**Paul Olufunsho**

## Repository

[View the GitHub Repository](https://github.com/019paul/cci-stem-connect-attendee-performance-system)

---

*CCI STEM Connect – Learn · Connect · Excel.*