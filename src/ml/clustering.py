
"""
CCI STEM Connect - K-Means Clustering Module

This module uses K-Means clustering to explore similarities
in attendee engagement and participation patterns.

IMPORTANT:
Cluster results are exploratory. They are not official
performance classifications or final attendee assessments.
"""

import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from .data_preparation import (
    CLUSTERING_FEATURES,
    prepare_clustering_data
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

DEFAULT_CLUSTERS = 3
DEFAULT_RANDOM_STATE = 42
DEFAULT_N_INIT = 10


# ============================================================
# 2. K-MEANS CLUSTERING
# ============================================================

def run_kmeans_clustering(
    data,
    n_clusters=DEFAULT_CLUSTERS,
    random_state=DEFAULT_RANDOM_STATE
):
    """
    Identify groups of attendees with similar engagement
    characteristics using K-Means clustering.

    Parameters:
        data:
            Attendee DataFrame containing the six assessment features.

        n_clusters:
            Number of groups to identify. Defaults to 3.

        random_state:
            Random seed for reproducibility.

    Returns:
        clustered_data:
            Original attendee records with an added cluster label.

        cluster_profiles:
            Summary of the characteristics of each cluster.

        metrics:
            Basic information about the clustering results.
    """

    # --------------------------------------------------------
    # Validate the cluster configuration
    # --------------------------------------------------------

    if isinstance(n_clusters, bool) or not isinstance(n_clusters, int):
        raise TypeError(
            "n_clusters must be an integer."
        )

    if isinstance(random_state, bool) or not isinstance(random_state, int):
        raise TypeError(
            "random_state must be an integer."
        )

    if n_clusters < 2:
        raise ValueError(
            "K-Means requires at least two clusters."
        )

    if len(data) <= n_clusters:
        raise ValueError(
            "The number of attendee records must be greater "
            "than the requested number of clusters."
        )

    # --------------------------------------------------------
    # Prepare and standardise attendee features
    # --------------------------------------------------------

    scaled_data, scaler = prepare_clustering_data(data)

    # --------------------------------------------------------
    # Initialise the K-Means model
    # --------------------------------------------------------

    clustering_model = KMeans(
        n_clusters=n_clusters,
        random_state=random_state,
        n_init=DEFAULT_N_INIT
    )

    # --------------------------------------------------------
    # Fit the model and assign cluster labels
    # --------------------------------------------------------

    cluster_labels = clustering_model.fit_predict(
        scaled_data
    )

    # Work with a copy of the original attendee records.
    clustered_data = data.copy().reset_index(drop=True)

    # Cluster labels are identifiers, not performance rankings.
    clustered_data["engagement_cluster"] = (
        cluster_labels + 1
    )

    # --------------------------------------------------------
    # Prepare cluster profiles
    # --------------------------------------------------------

    cluster_counts = (
        clustered_data
        .groupby("engagement_cluster")
        .size()
        .rename("attendee_count")
    )

    cluster_averages = (
        clustered_data
        .groupby("engagement_cluster")[CLUSTERING_FEATURES]
        .mean()
        .round(2)
    )

    cluster_profiles = pd.concat(
        [
            cluster_counts,
            cluster_averages
        ],
        axis=1
    ).reset_index()

    # Add the average official score as descriptive information
    # only. It is NOT used as an input to K-Means.
    if "performance_score" in clustered_data.columns:

        average_performance = (
            clustered_data
            .groupby("engagement_cluster")["performance_score"]
            .mean()
            .round(2)
            .rename("average_performance_score")
        )

        cluster_profiles = cluster_profiles.merge(
            average_performance,
            on="engagement_cluster",
            how="left"
        )

    # --------------------------------------------------------
    # Calculate cluster evaluation information
    # --------------------------------------------------------

    actual_clusters = len(
        set(cluster_labels)
    )

    silhouette = None

    # Silhouette score requires at least two actual clusters,
    # and fewer clusters than individual records.
    if 2 <= actual_clusters < len(clustered_data):

        try:

            silhouette = round(
                float(
                    silhouette_score(
                        scaled_data,
                        cluster_labels
                    )
                ),
                4
            )

        except ValueError:
            silhouette = None

    # --------------------------------------------------------
    # Create clustering metrics
    # --------------------------------------------------------

    cluster_sizes = {
        int(cluster_id): int(count)
        for cluster_id, count in (
            clustered_data["engagement_cluster"]
            .value_counts()
            .sort_index()
            .items()
        )
    }

    metrics = {
        "total_attendees": len(clustered_data),
        "requested_clusters": n_clusters,
        "actual_clusters": actual_clusters,
        "inertia": round(
            float(clustering_model.inertia_),
            4
        ),
        "silhouette_score": silhouette,
        "cluster_sizes": cluster_sizes,
        "random_state": random_state
    }

    return (
        clustered_data,
        cluster_profiles,
        metrics
    )


# ============================================================
# 3. DISPLAY CLUSTERING SUMMARY
# ============================================================

def generate_clustering_summary(metrics):
    """
    Produce a readable summary of the clustering results.
    """

    summary = {
        "Total Attendees": metrics["total_attendees"],
        "Requested Clusters": metrics["requested_clusters"],
        "Actual Clusters": metrics["actual_clusters"],
        "Inertia": metrics["inertia"],
        "Silhouette Score": metrics["silhouette_score"],
        "Cluster Sizes": metrics["cluster_sizes"]
    }

    return summary
