
"""
CCI STEM Connect - Machine Learning Model Evaluation

This module evaluates:

1. Random Forest classification performance.
2. K-Means clustering quality.

Evaluation metrics are reported separately.
"""

import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
    roc_auc_score,
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score
)


# ============================================================
# 1. RANDOM FOREST CLASSIFICATION EVALUATION
# ============================================================

def evaluate_classifier(
    y_true,
    y_pred,
    y_probability=None
):
    """
    Evaluate a binary classification model.

    Parameters:
        y_true:
            Actual attendance outcomes.

        y_pred:
            Predicted attendance outcomes.

        y_probability:
            Optional predicted probabilities for class 1.

    Returns:
        Dictionary containing classification metrics.
    """

    actual = np.asarray(y_true)
    predicted = np.asarray(y_pred)

    if len(actual) == 0:
        raise ValueError("Actual outcomes cannot be empty.")

    if len(actual) != len(predicted):
        raise ValueError(
            "Actual and predicted outcomes must have equal lengths."
        )

    if not np.isin(actual, [0, 1]).all():
        raise ValueError(
            "Actual outcomes must contain only 0 and 1."
        )

    if not np.isin(predicted, [0, 1]).all():
        raise ValueError(
            "Predicted outcomes must contain only 0 and 1."
        )

    if len(np.unique(actual)) < 2:
        raise ValueError(
            "Evaluation requires both actual outcome classes."
        )

    # Calculate classification metrics.
    accuracy = accuracy_score(actual, predicted)

    precision = precision_score(
        actual,
        predicted,
        pos_label=1,
        zero_division=0
    )

    recall = recall_score(
        actual,
        predicted,
        pos_label=1,
        zero_division=0
    )

    f1 = f1_score(
        actual,
        predicted,
        pos_label=1,
        zero_division=0
    )

    confusion = confusion_matrix(
        actual,
        predicted,
        labels=[0, 1]
    )

    report = classification_report(
        actual,
        predicted,
        labels=[0, 1],
        target_names=[
            "Did Not Attend",
            "Attended"
        ],
        output_dict=True,
        zero_division=0
    )

    metrics = {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": confusion.tolist(),
        "classification_report": report
    }

    # Calculate ROC-AUC when probabilities are supplied.
    if y_probability is not None:

        probabilities = np.asarray(y_probability)

        if len(probabilities) != len(actual):
            raise ValueError(
                "Probability and actual outcome lengths must match."
            )

        if (
            not np.isfinite(probabilities).all()
            or (probabilities < 0).any()
            or (probabilities > 1).any()
        ):
            raise ValueError(
                "Probabilities must be finite values between 0 and 1."
            )

        metrics["roc_auc"] = round(
            float(
                roc_auc_score(actual, probabilities)
            ),
            4
        )

    return metrics


# ============================================================
# 2. K-MEANS CLUSTERING EVALUATION
# ============================================================

def evaluate_clustering(features, cluster_labels):
    """
    Evaluate K-Means clustering quality.

    Metrics:
        - Silhouette score
        - Davies-Bouldin index
        - Calinski-Harabasz score
        - Number of clusters
        - Cluster sizes

    Higher silhouette scores generally indicate better separation.
    Lower Davies-Bouldin scores generally indicate better separation.
    Higher Calinski-Harabasz scores generally indicate better-defined
    clusters.

    These metrics do not establish business usefulness by themselves.
    """

    X = np.asarray(features)

    labels = np.asarray(cluster_labels)

    if X.ndim != 2:
        raise ValueError(
            "Clustering features must be a two-dimensional array."
        )

    if len(X) != len(labels):
        raise ValueError(
            "Feature records and cluster labels must have equal lengths."
        )

    if len(X) < 3:
        raise ValueError(
            "At least three records are required for this evaluation."
        )

    if not np.isfinite(X).all():
        raise ValueError(
            "Clustering features contain missing or infinite values."
        )

    if pd.isna(labels).any():
        raise ValueError(
            "Cluster labels contain missing values."
        )

    unique_clusters = np.unique(labels)

    number_of_clusters = len(unique_clusters)

    if number_of_clusters < 2:
        raise ValueError(
            "At least two clusters are required."
        )

    if number_of_clusters >= len(X):
        raise ValueError(
            "The number of clusters must be smaller "
            "than the number of records."
        )

    # Calculate clustering quality metrics.
    silhouette = silhouette_score(
        X,
        labels
    )

    davies_bouldin = davies_bouldin_score(
        X,
        labels
    )

    calinski_harabasz = calinski_harabasz_score(
        X,
        labels
    )

    # Calculate the number of attendees in each cluster.
    cluster_counts = (
        pd.Series(labels)
        .value_counts()
        .sort_index()
    )

    cluster_sizes = {
        int(cluster): int(count)
        for cluster, count in cluster_counts.items()
    }

    results = {
        "total_records": len(X),

        "number_of_clusters": number_of_clusters,

        "silhouette_score": round(
            float(silhouette), 4
        ),

        "davies_bouldin_index": round(
            float(davies_bouldin), 4
        ),

        "calinski_harabasz_score": round(
            float(calinski_harabasz), 4
        ),

        "cluster_sizes": cluster_sizes
    }

    return results


# ============================================================
# 3. GENERATE MODEL EVALUATION REPORT
# ============================================================

def generate_evaluation_report(results, model_name):
    """
    Convert model evaluation results into a readable
    Pandas DataFrame.
    """

    report = pd.DataFrame(
        [
            {
                "Model": model_name,
                "Metric": metric,
                "Value": value
            }
            for metric, value in results.items()
            if not isinstance(value, (dict, list))
        ]
    )

    return report


# ============================================================
# 4. MODEL EVALUATION INFORMATION
# ============================================================

def get_evaluation_metrics():

    return {
        "classification": [
            "Accuracy",
            "Precision",
            "Recall",
            "F1 Score",
            "ROC-AUC",
            "Confusion Matrix"
        ],

        "clustering": [
            "Silhouette Score",
            "Davies-Bouldin Index",
            "Calinski-Harabasz Score",
            "Cluster Distribution"
        ]
    }
