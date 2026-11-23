
"""
CCI STEM Connect - Random Forest Classification Module

Purpose:
Predict whether an attendee will attend a subsequent
CCI STEM Connect event.

Target:
1 = Attended the next event
0 = Did not attend the next event

IMPORTANT:
This model requires genuine historical attendance outcomes.
The current 14-attendee dataset cannot train this model yet.
"""

import math

import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from .data_preparation import (
    RANDOM_FOREST_FEATURES,
    validate_numeric_features,
    prepare_random_forest_data
)


# ============================================================
# 1. MODEL CONFIGURATION
# ============================================================

RANDOM_STATE = 42

N_ESTIMATORS = 300

MAX_DEPTH = 6

MIN_SAMPLES_LEAF = 2


# ============================================================
# 2. CHRONOLOGICAL DATA SPLITTING
# ============================================================

def chronological_split(
    X,
    y,
    metadata,
    test_fraction=0.20
):
    """
    Split historical records by event date.

    Earlier event records are used for training.
    Later event records are reserved for testing.

    This avoids randomly mixing future event records
    into the historical training period.
    """

    if not 0 < test_fraction < 0.5:
        raise ValueError(
            "test_fraction must be greater than 0 "
            "and less than 0.5."
        )

    unique_dates = sorted(
        metadata["event_date"].unique()
    )

    if len(unique_dates) < 3:

        raise ValueError(
            "At least three distinct historical event dates "
            "are required for this chronological training "
            "and testing approach. More events are recommended."
        )

    number_of_test_dates = max(
        1,
        math.ceil(len(unique_dates) * test_fraction)
    )

    number_of_training_dates = (
        len(unique_dates) - number_of_test_dates
    )

    if number_of_training_dates < 2:

        raise ValueError(
            "Not enough historical event dates remain "
            "for training. Add more event history."
        )

    test_start_date = unique_dates[
        number_of_training_dates
    ]

    train_mask = (
        metadata["event_date"] < test_start_date
    )

    test_mask = (
        metadata["event_date"] >= test_start_date
    )

    X_train = X.loc[train_mask].copy()
    X_test = X.loc[test_mask].copy()

    y_train = y.loc[train_mask].copy()
    y_test = y.loc[test_mask].copy()

    train_metadata = metadata.loc[train_mask].copy()
    test_metadata = metadata.loc[test_mask].copy()

    if X_train.empty or X_test.empty:

        raise ValueError(
            "The chronological split produced an empty "
            "training or testing dataset."
        )

    if y_train.nunique() < 2:

        raise ValueError(
            "The historical training period must contain "
            "both attendance outcomes: attended and did not attend."
        )

    if y_test.nunique() < 2:

        raise ValueError(
            "The testing period must contain both attendance "
            "outcomes to calculate meaningful binary "
            "classification metrics. More historical "
            "attendance records are needed."
        )

    return (
        X_train,
        X_test,
        y_train,
        y_test,
        train_metadata,
        test_metadata
    )


# ============================================================
# 3. TRAIN RANDOM FOREST CLASSIFIER
# ============================================================

def train_random_forest_model(
    historical_data,
    test_fraction=0.20,
    random_state=RANDOM_STATE
):
    """
    Train and evaluate a Random Forest classifier.

    Input:
        Historical attendee records containing:
        - attendee_id
        - event_id
        - event_date
        - Six assessment features
        - attended_next_event

    Returns:
        model
        metrics
        feature_importance
        test_predictions

    The function refuses to train when historical
    attendance labels are missing or insufficient.
    """

    # --------------------------------------------------------
    # Prepare historical data
    # --------------------------------------------------------

    X, y, metadata = prepare_random_forest_data(
        historical_data
    )

    # --------------------------------------------------------
    # Split historical data chronologically
    # --------------------------------------------------------

    (
        X_train,
        X_test,
        y_train,
        y_test,
        train_metadata,
        test_metadata
    ) = chronological_split(
        X,
        y,
        metadata,
        test_fraction=test_fraction
    )

    # --------------------------------------------------------
    # Configure Random Forest
    # --------------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        max_depth=MAX_DEPTH,
        min_samples_leaf=MIN_SAMPLES_LEAF,
        class_weight="balanced_subsample",
        random_state=random_state,
        n_jobs=-1
    )

    # --------------------------------------------------------
    # Train model using historical training data
    # --------------------------------------------------------

    model.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # Predict outcomes in the reserved test period
    # --------------------------------------------------------

    predictions = model.predict(
        X_test
    )

    # --------------------------------------------------------
    # Obtain probabilities of subsequent attendance
    # --------------------------------------------------------

    class_position = list(
        model.classes_
    ).index(1)

    probabilities = model.predict_proba(
        X_test
    )[:, class_position]

    # --------------------------------------------------------
    # Calculate evaluation metrics
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        pos_label=1,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        pos_label=1,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        pos_label=1,
        zero_division=0
    )

    confusion = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1]
    )

    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=[
            "Did Not Attend",
            "Attended"
        ],
        output_dict=True,
        zero_division=0
    )

    # --------------------------------------------------------
    # Prepare evaluation results
    # --------------------------------------------------------

    metrics = {

        "accuracy": round(float(accuracy), 4),

        "precision": round(float(precision), 4),

        "recall": round(float(recall), 4),

        "f1_score": round(float(f1), 4),

        "training_records": len(X_train),

        "testing_records": len(X_test),

        "training_start_date": str(
            train_metadata["event_date"].min().date()
        ),

        "training_end_date": str(
            train_metadata["event_date"].max().date()
        ),

        "testing_start_date": str(
            test_metadata["event_date"].min().date()
        ),

        "testing_end_date": str(
            test_metadata["event_date"].max().date()
        ),

        "confusion_matrix": confusion.tolist(),

        "classification_report": report
    }

    # --------------------------------------------------------
    # Calculate feature importance
    # --------------------------------------------------------

    feature_importance = pd.DataFrame({

        "feature": RANDOM_FOREST_FEATURES,

        "importance": model.feature_importances_

    }).sort_values(
        by="importance",
        ascending=False
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Prepare test predictions
    # --------------------------------------------------------

    test_predictions = test_metadata.copy()

    test_predictions["actual_outcome"] = (
        y_test.values
    )

    test_predictions["predicted_outcome"] = (
        predictions
    )

    test_predictions["attendance_probability"] = (
        probabilities.round(4)
    )

    test_predictions["predicted_label"] = (
        test_predictions["predicted_outcome"]
        .map({
            1: "Likely to Attend",
            0: "Not Predicted to Attend"
        })
    )

    return (
        model,
        metrics,
        feature_importance,
        test_predictions
    )


# ============================================================
# 4. PREDICT FUTURE ATTENDANCE
# ============================================================

def predict_next_event_attendance(
    model,
    attendee_data
):
    """
    Predict subsequent event attendance for new attendee
    records using a previously trained Random Forest model.

    The supplied records must contain the six assessment
    features used during model training.
    """

    # Validate the six input features
    cleaned_data = validate_numeric_features(
        attendee_data,
        RANDOM_FOREST_FEATURES
    )

    # Predict attendance outcomes
    predictions = model.predict(
        cleaned_data[RANDOM_FOREST_FEATURES]
    )

    class_position = list(
        model.classes_
    ).index(1)

    probabilities = model.predict_proba(
        cleaned_data[RANDOM_FOREST_FEATURES]
    )[:, class_position]

    results = attendee_data.copy()

    results["predicted_attended_next_event"] = (
        predictions
    )

    results["attendance_probability"] = (
        probabilities.round(4)
    )

    results["prediction_label"] = (
        results["predicted_attended_next_event"]
        .map({
            1: "Likely to Attend",
            0: "Not Predicted to Attend"
        })
    )

    return results


# ============================================================
# 5. RANDOM FOREST MODEL INFORMATION
# ============================================================

def get_random_forest_model_info():

    return {

        "model_name": "Random Forest Classifier",

        "learning_type": "Supervised Learning",

        "prediction_target": "attended_next_event",

        "positive_class": "Attended",

        "negative_class": "Did Not Attend",

        "features": RANDOM_FOREST_FEATURES,

        "estimators": N_ESTIMATORS,

        "random_state": RANDOM_STATE,

        "status": "Experimental - Historical labels required"
    }
