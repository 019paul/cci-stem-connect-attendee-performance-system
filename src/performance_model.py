
import pandas as pd
from pathlib import Path


# ============================================================
# 1. PROJECT PATHS AND CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "cci_attendees.csv"

SAMPLE_DATA_FILE = (
    BASE_DIR / "sample_data" / "cci_attendees_sample.csv"
)

OUTPUT_DIR = BASE_DIR / "outputs"


# Required input columns
REQUIRED_COLUMNS = [
    "attendee_id",
    "attendee_name",
    "category",
    "attendance_rate",
    "session_participation",
    "practical_engagement",
    "teamwork",
    "activities_completed",
    "feedback_score"
]


# Permitted score ranges
SCORE_RANGES = {
    "attendance_rate": (0, 100),
    "session_participation": (0, 10),
    "practical_engagement": (0, 10),
    "teamwork": (0, 10),
    "activities_completed": (0, 100),
    "feedback_score": (0, 10)
}


# Valid attendee categories
VALID_CATEGORIES = [
    "Student",
    "Mentor",
    "Facilitator"
]


# Performance categories
PERFORMANCE_CATEGORIES = [
    "Outstanding",
    "Excellent",
    "Good",
    "Average",
    "Needs Improvement"
]


# ============================================================
# 2. DATA VALIDATION
# ============================================================

def validate_data(data):
    """
    Validate attendee records before performance evaluation.

    Checks:
    - Required columns
    - Empty datasets
    - Missing and blank values
    - Duplicate attendee IDs
    - Numeric values
    - Permitted score ranges
    - Valid attendee categories

    Returns a cleaned DataFrame.
    """

    # Confirm that input is a DataFrame
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            "Attendee data must be a Pandas DataFrame."
        )

    # Check required columns
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Check for an empty dataset
    if data.empty:
        raise ValueError(
            "The attendee dataset is empty."
        )

    # Work on a copy to protect the original data
    data = data.copy()

    errors = []

    # Clean text fields
    text_columns = [
        "attendee_id",
        "attendee_name",
        "category"
    ]

    for column in text_columns:

        data[column] = (
            data[column]
            .astype("string")
            .str.strip()
        )

    # Check missing and blank values
    for column in REQUIRED_COLUMNS:

        blank_values = (
            data[column]
            .astype("string")
            .str.strip()
            .eq("")
            .fillna(False)
        )

        missing_values = (
            data[column].isna()
            | blank_values
        )

        for position in range(len(data)):

            if missing_values.iloc[position]:

                errors.append(
                    f"Data row {position + 2}: "
                    f"'{column}' cannot be blank."
                )

    # Check duplicate attendee IDs
    valid_ids = data["attendee_id"].dropna()

    valid_ids = valid_ids[
        valid_ids != ""
    ]

    duplicate_ids = valid_ids[
        valid_ids.duplicated(keep=False)
    ].unique()

    for attendee_id in duplicate_ids:

        errors.append(
            f"Duplicate attendee ID found: {attendee_id}"
        )

    # Convert and validate numeric columns
    numeric_columns = [
        "attendance_rate",
        "session_participation",
        "practical_engagement",
        "teamwork",
        "activities_completed",
        "feedback_score"
    ]

    for column in numeric_columns:

        original_values = data[column].copy()

        converted_values = pd.to_numeric(
            original_values,
            errors="coerce"
        )

        original_text = (
            original_values
            .astype("string")
            .str.strip()
        )

        nonblank_values = (
            original_values.notna()
            & original_text.ne("").fillna(False)
        )

        invalid_values = (
            converted_values.isna()
            & nonblank_values
        )

        for position in range(len(data)):

            if invalid_values.iloc[position]:

                errors.append(
                    f"Data row {position + 2}: "
                    f"'{column}' must contain a valid number."
                )

        data[column] = converted_values

    # Check permitted score ranges
    for column, (minimum, maximum) in SCORE_RANGES.items():

        for position in range(len(data)):

            value = data[column].iloc[position]

            if pd.notna(value):

                if not minimum <= value <= maximum:

                    errors.append(
                        f"Data row {position + 2}: "
                        f"'{column}' must be between "
                        f"{minimum} and {maximum}. "
                        f"Found: {value}"
                    )

    # Normalize and validate attendee categories
    category_lookup = {
        category.casefold(): category
        for category in VALID_CATEGORIES
    }

    for position in range(len(data)):

        category = data["category"].iloc[position]

        if pd.notna(category) and category != "":

            normalized_category = category_lookup.get(
                category.casefold()
            )

            if normalized_category is None:

                errors.append(
                    f"Data row {position + 2}: "
                    f"Invalid category '{category}'. "
                    f"Allowed categories: {VALID_CATEGORIES}"
                )

            else:

                data.iat[
                    position,
                    data.columns.get_loc("category")
                ] = normalized_category

    # Display all detected validation errors
    if errors:

        error_message = "\n".join(
            f"- {error}"
            for error in errors
        )

        raise ValueError(
            "Data validation failed:\n" + error_message
        )

    return data


# ============================================================
# 3. PERFORMANCE CLASSIFICATION
# ============================================================

def classify_performance(score):
    """
    Assign a performance category based on the final score.
    """

    if score >= 90:
        return "Outstanding"

    elif score >= 75:
        return "Excellent"

    elif score >= 60:
        return "Good"

    elif score >= 40:
        return "Average"

    else:
        return "Needs Improvement"


# ============================================================
# 4. ATTENDEE PERFORMANCE EVALUATION
# ============================================================

def evaluate_attendee_data(data):
    """
    Validate attendee data, calculate performance scores,
    assign performance categories, and rank attendees.

    Accepts a Pandas DataFrame from CSV, Excel or an upload.
    """

    # Validate the supplied attendee data
    data = validate_data(data)

    # Convert scores out of 10 into percentages
    data["session_percentage"] = (
        data["session_participation"] * 10
    )

    data["practical_percentage"] = (
        data["practical_engagement"] * 10
    )

    data["teamwork_percentage"] = (
        data["teamwork"] * 10
    )

    data["feedback_percentage"] = (
        data["feedback_score"] * 10
    )

    # Calculate weighted performance score
    data["performance_score"] = (
        data["attendance_rate"] * 0.20
        + data["session_percentage"] * 0.15
        + data["practical_percentage"] * 0.20
        + data["teamwork_percentage"] * 0.15
        + data["activities_completed"] * 0.20
        + data["feedback_percentage"] * 0.10
    )

    # Round performance scores to two decimal places
    data["performance_score"] = (
        data["performance_score"].round(2)
    )

    # Assign performance categories
    data["performance_category"] = (
        data["performance_score"].apply(
            classify_performance
        )
    )

    # Rank attendees from highest to lowest score
    data["rank"] = (
        data["performance_score"]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )

    # Sort attendees by performance rank
    data = data.sort_values(
        by=["rank", "attendee_name"]
    ).reset_index(drop=True)

    return data


# ============================================================
# 5. LOAD THE ORIGINAL OR SAMPLE DATASET
# ============================================================

def evaluate_attendees():
    """
    Load and evaluate attendee data.

    Priority:
    1. Use the private company CSV when it exists.
    2. Otherwise, use the fictional GitHub sample dataset.

    The original company dataset is never overwritten.
    """

    if DATA_FILE.exists():

        input_file = DATA_FILE

        source_description = "Original company dataset"

    elif SAMPLE_DATA_FILE.exists():

        input_file = SAMPLE_DATA_FILE

        source_description = "Sample demonstration dataset"

    else:

        raise FileNotFoundError(
            "No attendee dataset was found.\n"
            "Expected either:\n"
            f"- {DATA_FILE}\n"
            f"- {SAMPLE_DATA_FILE}"
        )

    # Load CSV dataset
    data = pd.read_csv(input_file)

    # Evaluate attendee performance
    data = evaluate_attendee_data(data)

    print("Data validation completed successfully!")

    print(f"Dataset source: {source_description}")

    return data


# ============================================================
# 6. EVENT SUMMARY
# ============================================================

def generate_event_summary(data):
    """
    Generate overall CCI STEM Connect event statistics.
    """

    if data.empty:

        raise ValueError(
            "Cannot generate a summary from an empty dataset."
        )

    total_attendees = len(data)

    average_score = data["performance_score"].mean()

    highest_score = data["performance_score"].max()

    lowest_score = data["performance_score"].min()

    top_attendee = data.loc[
        data["performance_score"].idxmax()
    ]

    lowest_attendee = data.loc[
        data["performance_score"].idxmin()
    ]

    summary = {

        "Total Attendees": total_attendees,

        "Average Performance Score": round(
            average_score, 2
        ),

        "Highest Performance Score": highest_score,

        "Lowest Performance Score": lowest_score,

        "Top Performing Attendee": (
            f"{top_attendee['attendee_name']} - "
            f"{top_attendee['performance_score']}"
        ),

        "Lowest Performing Attendee": (
            f"{lowest_attendee['attendee_name']} - "
            f"{lowest_attendee['performance_score']}"
        )
    }

    return summary


# ============================================================
# 7. PERFORMANCE CATEGORY DISTRIBUTION
# ============================================================

def generate_performance_distribution(data):
    """
    Count attendees in each performance category.
    """

    distribution = (
        data["performance_category"]
        .value_counts()
        .reindex(
            PERFORMANCE_CATEGORIES,
            fill_value=0
        )
    )

    distribution = distribution.rename_axis(
        "performance_category"
    ).reset_index(name="attendee_count")

    return distribution


# ============================================================
# 8. EXPORT REPORTS
# ============================================================

def export_reports(data):
    """
    Export attendee results, event summary and category
    distribution into separate CSV reports.
    """

    # Create output folder if it does not exist
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Generate reports
    summary = generate_event_summary(data)

    distribution = generate_performance_distribution(data)

    # Export attendee performance report
    attendee_report_path = (
        OUTPUT_DIR / "cci_attendee_performance.csv"
    )

    data.to_csv(
        attendee_report_path,
        index=False
    )

    # Export event summary report
    summary_report_path = (
        OUTPUT_DIR / "cci_event_summary.csv"
    )

    summary_df = pd.DataFrame(
        list(summary.items()),
        columns=["Metric", "Value"]
    )

    summary_df.to_csv(
        summary_report_path,
        index=False
    )

    # Export performance distribution report
    distribution_report_path = (
        OUTPUT_DIR / "cci_performance_distribution.csv"
    )

    distribution.to_csv(
        distribution_report_path,
        index=False
    )

    print("\nReports exported successfully!")

    print(f"Attendee report: {attendee_report_path}")

    print(f"Event summary: {summary_report_path}")

    print(
        f"Performance distribution: {distribution_report_path}"
    )


# ============================================================
# 9. MAIN PROGRAM
# ============================================================

def main():

    # Evaluate attendee performance
    data = evaluate_attendees()

    # Display attendee performance results
    print("\nCCI STEM Connect Performance Results")

    print(
        data[
            [
                "rank",
                "attendee_id",
                "attendee_name",
                "performance_score",
                "performance_category"
            ]
        ].to_string(index=False)
    )

    # Generate event summary
    summary = generate_event_summary(data)

    print("\nCCI STEM Connect Overall Event Summary")

    for metric, value in summary.items():

        print(f"{metric}: {value}")

    # Display performance category distribution
    distribution = generate_performance_distribution(data)

    print("\nPerformance Category Distribution")

    for _, row in distribution.iterrows():

        print(
            f"{row['performance_category']}: "
            f"{row['attendee_count']}"
        )

    # Export reports
    export_reports(data)


# ============================================================
# 10. PROGRAM EXECUTION
# ============================================================

if __name__ == "__main__":
    main()
