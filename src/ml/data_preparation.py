
"""
CCI STEM Connect - Machine Learning Data Preparation

This module prepares attendee information for:

1. Random Forest classification
2. K-Means engagement clustering

The existing rule-based performance scoring model
remains separate and unchanged.
"""

import pandas as pd

from sklearn.preprocessing import StandardScaler


# ============================================================
# 1. CONFIGURATION
# ============================================================

# Existing assessment features
CLUSTERING_FEATURES = [
    "attendance_rate",
    "session_participation",
    "practical_engagement",
    "teamwork",
    "activities_completed",
    "feedback_score"
]

# Features used by the Random Forest model
RANDOM_FOREST_FEATURES = [
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

# Target variable for Random Forest
TARGET_COLUMN = "attended_next_event"

# Required historical data columns
HISTORICAL_REQUIRED_COLUMNS = [
    "attendee_id",
    "event_id",
    "event_date",
    *RANDOM_FOREST_FEATURES,
    TARGET_COLUMN
]


# ============================================================
# 2. COMMON COLUMN VALIDATION
# ============================================================

def check_required_columns(data, required_columns):
    """
    Check whether all required columns are present.
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            "Input must be a Pandas DataFrame."
        )

    if data.empty:
        raise ValueError(
            "The supplied dataset is empty."
        )

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


# ============================================================
# 3. NUMERICAL FEATURE VALIDATION
# ============================================================

def validate_numeric_features(data, features):
    """
    Validate numerical assessment features.

    Checks:
    - Missing values
    - Non-numeric values
    - Permitted score ranges

    Returns a cleaned DataFrame.
    """

    cleaned_data = data.copy()

    errors = []

    for column in features:

        values = cleaned_data[column]

        converted = pd.to_numeric(
            values,
            errors="coerce"
        )

        invalid = converted.isna()

        if invalid.any():

            positions = [
                position + 2
                for position, invalid_value
                in enumerate(invalid)
                if invalid_value
            ]

            errors.append(
                f"'{column}' contains missing or invalid "
                f"values in data rows: {positions}"
            )

        minimum, maximum = SCORE_RANGES[column]

        out_of_range = (
            converted.notna()
            & (
                (converted < minimum)
                | (converted > maximum)
            )
        )

        if out_of_range.any():

            errors.append(
                f"'{column}' must be between "
                f"{minimum} and {maximum}."
            )

        cleaned_data[column] = converted

    if errors:

        raise ValueError(
            "Feature validation failed:\n"
            + "\n".join(f"- {error}" for error in errors)
        )

    return cleaned_data


# ============================================================
# 4. DATA PREPARATION FOR K-MEANS CLUSTERING
# ============================================================

def prepare_clustering_data(data):
    """
    Prepare attendee assessment data for K-Means.

    Steps:
    1. Check required features.
    2. Validate numerical values.
    3. Standardize numerical features.

    Returns:
        scaled_data: Standardized feature DataFrame.
        scaler: Fitted StandardScaler.

    Note:
        Standardization is important because the input
        features use different score ranges.
    """

    check_required_columns(
        data,
        CLUSTERING_FEATURES
    )

    cleaned_data = validate_numeric_features(
        data,
        CLUSTERING_FEATURES
    )

    scaler = StandardScaler()

    scaled_values = scaler.fit_transform(
        cleaned_data[CLUSTERING_FEATURES]
    )

    scaled_data = pd.DataFrame(
        scaled_values,
        columns=CLUSTERING_FEATURES,
        index=cleaned_data.index
    )

    return scaled_data, scaler


# ============================================================
# 5. DATA PREPARATION FOR RANDOM FOREST
# ============================================================

def prepare_random_forest_data(data):
    """
    Prepare historical attendee records for Random Forest.

    Required historical information:

    - attendee_id
    - event_id
    - event_date
    - six assessment features
    - attended_next_event

    Target:
        1 = Attendee attended the subsequent event.
        0 = Attendee did not attend the subsequent event.

    Returns:
        X: Numerical input features.
        y: Target variable.
        metadata: Attendee IDs, event IDs and event dates.

    Important:
        Each training row must represent an attendee's
        previous event, with a verified outcome for the
        subsequent event.
    """

    check_required_columns(
        data,
        HISTORICAL_REQUIRED_COLUMNS
    )

    cleaned_data = data.copy()

    # --------------------------------------------------------
    # Validate attendee and event identifiers
    # --------------------------------------------------------

    for column in ["attendee_id", "event_id"]:

        cleaned_data[column] = (
            cleaned_data[column]
            .astype("string")
            .str.strip()
        )

        if (
            cleaned_data[column].isna().any()
            or cleaned_data[column].eq("").any()
        ):

            raise ValueError(
                f"'{column}' contains missing or blank values."
            )

    # Each attendee must have only one record per event.
    duplicates = cleaned_data.duplicated(
        subset=["attendee_id", "event_id"],
        keep=False
    )

    if duplicates.any():

        raise ValueError(
            "Duplicate attendee and event combinations found."
        )

    # --------------------------------------------------------
    # Validate event dates
    # --------------------------------------------------------

    cleaned_data["event_date"] = pd.to_datetime(
        cleaned_data["event_date"],
        errors="coerce"
    )

    if cleaned_data["event_date"].isna().any():

        raise ValueError(
            "'event_date' contains missing or invalid dates."
        )

    # --------------------------------------------------------
    # Validate numerical features
    # --------------------------------------------------------

    cleaned_data = validate_numeric_features(
        cleaned_data,
        RANDOM_FOREST_FEATURES
    )

    # --------------------------------------------------------
    # Validate the prediction target
    # --------------------------------------------------------

    target_lookup = {
        "1": 1,
        "0": 0,
        "1.0": 1,
        "0.0": 0,
        "yes": 1,
        "no": 0,
        "true": 1,
        "false": 0,
        "attended": 1,
        "did not attend": 0,
        "not attended": 0
    }

    target_values = (
        cleaned_data[TARGET_COLUMN]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    y = target_values.map(target_lookup)

    if y.isna().any():

        raise ValueError(
            "'attended_next_event' must contain "
            "1/0, Yes/No, True/False, "
            "Attended/Did not attend."
        )

    y = y.astype(int).rename(TARGET_COLUMN)

    if y.nunique() < 2:

        raise ValueError(
            "Random Forest training requires both "
            "attendance outcomes: 1 and 0."
        )

    # --------------------------------------------------------
    # Separate input features from metadata
    # --------------------------------------------------------

    X = cleaned_data[
        RANDOM_FOREST_FEATURES
    ].copy()

    metadata = cleaned_data[
        [
            "attendee_id",
            "event_id",
            "event_date"
        ]
    ].copy()

    return X, y, metadata


# ============================================================
# 6. MODULE INFORMATION
# ============================================================

def get_data_preparation_info():
    """
    Return a description of the prepared ML features.
    """

    return {
        "clustering_features": CLUSTERING_FEATURES,
        "random_forest_features": RANDOM_FOREST_FEATURES,
        "prediction_target": TARGET_COLUMN,
        "number_of_features": len(CLUSTERING_FEATURES)
    }
