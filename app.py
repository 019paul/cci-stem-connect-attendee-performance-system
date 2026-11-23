
import sys
import io
import html
import logging
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
OUTPUT_DIR = BASE_DIR / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SRC_DIR))

from performance_model import evaluate_attendees, validate_data


logging.basicConfig(
    filename=OUTPUT_DIR / "application.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("cci_stem_connect")


st.set_page_config(
    page_title="CCI STEM Connect | Attendance & Performance",
    page_icon="∞",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. BRAND IDENTITY
# ============================================================

RED = "#F04438"
DARK_RED = "#D92D20"
NAVY = "#243247"
WHITE = "#FFFFFF"
LIGHT_GREY = "#F4F6F9"
GREY = "#667085"
GREEN = "#16A34A"
BLUE = "#2563EB"
ORANGE = "#D97706"

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


# ============================================================
# 3. PROFESSIONAL INTERFACE STYLING
# ============================================================

st.markdown(
    f"""
    <style>

    /* Main application */
    .stApp {{
        background: {LIGHT_GREY};
        color: {NAVY};
    }}

    [data-testid="stMain"] {{
        background: {LIGHT_GREY};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: {WHITE};
        border-right: 1px solid #E4E7EC;
        min-width: 270px;
    }}

    section[data-testid="stSidebar"] > div {{
        background: {WHITE};
    }}

    section[data-testid="stSidebar"] .stRadio label {{
        color: {NAVY};
        font-weight: 600;
    }}

    /* Main headings */
    .main-title {{
        color: {NAVY};
        font-size: 30px;
        font-weight: 800;
        letter-spacing: -0.7px;
        margin-bottom: 5px;
    }}

    .main-subtitle {{
        color: {GREY};
        font-size: 14px;
        margin-bottom: 25px;
    }}

    .section-title {{
        color: {NAVY};
        font-size: 19px;
        font-weight: 750;
        margin-top: 18px;
        margin-bottom: 12px;
    }}

    /* Welcome banner */
    .welcome-banner {{
        background: linear-gradient(115deg, {NAVY}, #354B69);
        padding: 28px;
        border-radius: 16px;
        color: white;
        margin-bottom: 22px;
    }}

    .welcome-banner h2 {{
        color: white;
        font-size: 27px;
        margin: 0 0 8px 0;
    }}

    .welcome-banner p {{
        color: #D0D5DD;
        margin: 0;
        font-size: 14px;
    }}

    .welcome-symbol {{
        color: {RED};
        font-size: 45px;
        font-weight: 800;
    }}

    /* Metric cards */
    .metric-card {{
        background: {WHITE};
        border: 1px solid #E4E7EC;
        border-radius: 14px;
        padding: 19px;
        min-height: 125px;
        box-shadow: 0 2px 7px rgba(36, 50, 71, 0.035);
    }}

    .metric-label {{
        color: {GREY};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}

    .metric-value {{
        color: {NAVY};
        font-size: 28px;
        font-weight: 800;
        margin-top: 12px;
    }}

    .metric-note {{
        color: {GREY};
        font-size: 11px;
        margin-top: 5px;
    }}

    /* Information cards */
    .info-card {{
        background: {WHITE};
        border: 1px solid #E4E7EC;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 12px;
    }}

    .info-card h3 {{
        color: {NAVY};
        margin-top: 5px;
    }}

    .info-label {{
        color: {GREY};
        font-size: 12px;
        font-weight: 700;
    }}

    /* Profile card */
    .profile-card {{
        background: {NAVY};
        border-radius: 16px;
        padding: 23px;
        color: white;
        margin-bottom: 15px;
    }}

    .profile-card h2 {{
        color: white;
        margin-bottom: 5px;
    }}

    .profile-card p {{
        color: #D0D5DD;
        margin: 0;
    }}

    /* Buttons */
    div.stButton > button {{
        background: {RED};
        color: white;
        border: 1px solid {RED};
        border-radius: 9px;
        font-weight: 650;
        min-height: 42px;
    }}

    div.stButton > button:hover {{
        background: {DARK_RED};
        color: white;
        border-color: {DARK_RED};
    }}

    div[data-testid="stDownloadButton"] button {{
        background: {NAVY};
        color: white;
        border-radius: 9px;
        border: 1px solid {NAVY};
        min-height: 42px;
    }}

    div[data-testid="stDownloadButton"] button:hover {{
        background: #354B69;
        color: white;
    }}

    /* Input fields */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {{
        border-radius: 8px;
    }}

    /* Tables and charts */
    div[data-testid="stDataFrame"] {{
        border: 1px solid #E4E7EC;
        border-radius: 10px;
        overflow: hidden;
    }}

    div[data-testid="stMetric"] {{
        background: white;
        border: 1px solid #E4E7EC;
        border-radius: 12px;
        padding: 14px;
    }}

    /* Progress bars */
    div[data-testid="stProgressBar"] > div > div {{
        background-color: {RED};
    }}

    /* Footer */
    footer {{
        visibility: hidden;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 4. REUSABLE INTERFACE COMPONENTS
# ============================================================

def display_logo():

    st.html(
        f"""
        <div style="
            text-align:center;
            padding:18px 5px 20px;
            background:white;
        ">
            <div style="
                color:{RED};
                font-size:58px;
                font-weight:800;
                line-height:1;
            ">∞</div>

            <div style="
                color:{NAVY};
                font-size:19px;
                font-weight:800;
                margin-top:8px;
            ">CCI STEM CONNECT</div>

            <div style="
                color:{GREY};
                font-size:9px;
                letter-spacing:2px;
                margin-top:5px;
            ">LEARN · CONNECT · EXCEL</div>
        </div>
        """
    )


def page_header(title, description):

    st.markdown(
        f"""
        <div class="main-title">{html.escape(title)}</div>
        <div class="main-subtitle">{html.escape(description)}</div>
        """,
        unsafe_allow_html=True
    )


def metric_card(label, value, note=""):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-note">{html.escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_title(title):

    st.markdown(
        f'<div class="section-title">{html.escape(title)}</div>',
        unsafe_allow_html=True
    )


def show_empty_message(message):

    st.info(message)


# ============================================================
# 5. DATA PROCESSING
# ============================================================

def calculate_performance(data):

    df = data.copy()

    numerical_columns = [
        "attendance_rate",
        "session_participation",
        "practical_engagement",
        "teamwork",
        "activities_completed",
        "feedback_score"
    ]

    for column in numerical_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    df["performance_score"] = (
        0.20 * df["attendance_rate"]
        + 0.15 * df["session_participation"] * 10
        + 0.20 * df["practical_engagement"] * 10
        + 0.15 * df["teamwork"] * 10
        + 0.20 * df["activities_completed"]
        + 0.10 * df["feedback_score"] * 10
    ).round(2)

    def classify(score):

        if score >= 90:
            return "Outstanding"
        elif score >= 75:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Average"

        return "Needs Improvement"

    df["performance_category"] = (
        df["performance_score"].apply(classify)
    )

    df["rank"] = (
        df["performance_score"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    return df.sort_values(
        ["performance_score", "attendee_name"],
        ascending=[False, True]
    ).reset_index(drop=True)


@st.cache_data
def load_company_data():

    result = evaluate_attendees()

    if not isinstance(result, pd.DataFrame):
        raise ValueError("Invalid company dataset.")

    missing = [
        column for column in REQUIRED_COLUMNS
        if column not in result.columns
    ]

    if missing:
        raise ValueError("Required dataset columns are missing.")

    return result


# ============================================================
# 6. SESSION STATE AND DATA LOADING
# ============================================================

if "active_data" not in st.session_state:
    st.session_state.active_data = None

if "data_source" not in st.session_state:
    st.session_state.data_source = "Original company dataset"

if st.session_state.active_data is None:

    try:
        st.session_state.active_data = load_company_data()

    except Exception:

        logger.exception("Company dataset loading failed.")

        st.error(
            "The dashboard could not load the attendee information. "
            "Please contact your system administrator."
        )

        st.stop()


df = st.session_state.active_data.copy()

if df.empty:
    st.warning("There are currently no attendee records to display.")
    st.stop()


# ============================================================
# 7. SIDEBAR
# ============================================================

PAGES = [
    "Overview",
    "Attendance Overview",
    "Attendee Performance",
    "Individual Profile",
    "Performance Analytics",
    "Programme Insights",
    "Reports & Downloads",
    "Data Management"
]

with st.sidebar:

    display_logo()

    st.divider()

    st.markdown("### MAIN MENU")

    page = st.radio(
        "Navigation",
        PAGES,
        key="dashboard_navigation",
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### CURRENT DATA")

    st.caption(st.session_state.data_source)

    st.caption(f"{len(df)} attendee records")

    st.divider()

    st.caption("CCI STEM Connect")
    st.caption("Attendance & Performance System")


# ============================================================
# 8. OVERVIEW DASHBOARD
# ============================================================

if page == "Overview":

    st.markdown(
        f"""
        <div class="welcome-banner">
            <div class="welcome-symbol">∞</div>
            <h2>Welcome to CCI STEM Connect</h2>
            <p>
                Monitor attendance, understand engagement and
                evaluate attendee performance.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    total = len(df)
    average = df["performance_score"].mean()
    highest = df["performance_score"].max()
    attendance = df["attendance_rate"].mean()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("TOTAL ATTENDEES", total, "Records in current dataset")

    with c2:
        metric_card("AVERAGE PERFORMANCE", f"{average:.2f}%", "Overall score")

    with c3:
        metric_card("HIGHEST PERFORMANCE", f"{highest:.2f}%", "Best recorded score")

    with c4:
        metric_card("AVERAGE ATTENDANCE", f"{attendance:.1f}%", "Attendance indicator")

    section_title("Programme Performance")

    left, right = st.columns([1.15, 1])

    with left:

        st.markdown(
            '<div class="info-card"><b>Performance distribution</b></div>',
            unsafe_allow_html=True
        )

        distribution = (
            df["performance_category"]
            .value_counts()
            .reindex(
                ["Outstanding", "Excellent", "Good", "Average", "Needs Improvement"],
                fill_value=0
            )
            .rename_axis("Category")
            .reset_index(name="Attendees")
        )

        st.bar_chart(
            distribution,
            x="Category",
            y="Attendees",
            color=RED
        )

    with right:

        st.markdown(
            '<div class="info-card"><b>Attendance performance</b></div>',
            unsafe_allow_html=True
        )

        st.metric(
            "Average Attendance Rate",
            f"{attendance:.1f}%"
        )

        st.progress(
            max(0.0, min(1.0, float(attendance) / 100))
        )

        st.caption(
            "Average attendance across the currently loaded dataset."
        )

        st.metric(
            "Average Practical Engagement",
            f"{df['practical_engagement'].mean():.1f}/10"
        )

        st.metric(
            "Average Teamwork",
            f"{df['teamwork'].mean():.1f}/10"
        )

    section_title("Top Performing Attendees")

    top_five = df.head(5)[
        [
            "rank",
            "attendee_name",
            "category",
            "performance_score",
            "performance_category"
        ]
    ]

    st.dataframe(
        top_five,
        width="stretch",
        hide_index=True
    )


# ============================================================
# 9. ATTENDANCE OVERVIEW
# ============================================================

elif page == "Attendance Overview":

    page_header(
        "Attendance Overview",
        "Monitor attendee attendance and participation."
    )

    average_attendance = df["attendance_rate"].mean()

    high_attendance = df[df["attendance_rate"] >= 90]
    moderate_attendance = df[
        (df["attendance_rate"] >= 70)
        & (df["attendance_rate"] < 90)
    ]
    low_attendance = df[df["attendance_rate"] < 70]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("TOTAL ATTENDEES", len(df))

    with c2:
        metric_card("AVERAGE ATTENDANCE", f"{average_attendance:.1f}%")

    with c3:
        metric_card("HIGH ATTENDANCE", len(high_attendance), "90% and above")

    with c4:
        metric_card("LOW ATTENDANCE", len(low_attendance), "Below 70%")

    section_title("Attendance Distribution")

    attendance_data = df[
        ["attendee_name", "attendance_rate"]
    ].sort_values("attendance_rate", ascending=False)

    st.bar_chart(
        attendance_data,
        x="attendee_name",
        y="attendance_rate",
        color=RED
    )

    section_title("Attendance Records")

    attendance_filter = st.selectbox(
        "Filter attendance",
        [
            "All Attendees",
            "High Attendance (90% and above)",
            "Moderate Attendance (70%–89%)",
            "Low Attendance (Below 70%)"
        ]
    )

    if attendance_filter == "High Attendance (90% and above)":
        attendance_view = high_attendance

    elif attendance_filter == "Moderate Attendance (70%–89%)":
        attendance_view = moderate_attendance

    elif attendance_filter == "Low Attendance (Below 70%)":
        attendance_view = low_attendance

    else:
        attendance_view = df

    st.dataframe(
        attendance_view[
            ["attendee_id", "attendee_name", "category", "attendance_rate"]
        ],
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "Download Attendance Records",
        data=attendance_view.to_csv(index=False).encode("utf-8"),
        file_name="cci_attendance_records.csv",
        mime="text/csv"
    )

    st.caption(
        "Attendance figures represent the attendance_rate field in the "
        "current dataset. This page does not create individual daily "
        "present or absent records."
    )


# ============================================================
# 10. ATTENDEE PERFORMANCE
# ============================================================

elif page == "Attendee Performance":

    page_header(
        "Attendee Performance",
        "Explore, filter and compare attendee performance."
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        categories = ["All"] + sorted(
            df["category"].dropna().astype(str).unique().tolist()
        )

        selected_category = st.selectbox(
            "Attendee category",
            categories
        )

    with col2:

        search = st.text_input(
            "Search by attendee name or ID",
            placeholder="Enter a name or attendee ID..."
        )

    filtered = df.copy()

    if selected_category != "All":
        filtered = filtered[
            filtered["category"].astype(str) == selected_category
        ]

    if search:

        filtered = filtered[
            filtered["attendee_name"].astype(str).str.contains(
                search, case=False, na=False
            )
            |
            filtered["attendee_id"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("MATCHING ATTENDEES", len(filtered))

    with c2:
        metric_card(
            "AVERAGE SCORE",
            f"{filtered['performance_score'].mean():.2f}%"
            if not filtered.empty else "N/A"
        )

    with c3:
        metric_card(
            "AVERAGE ATTENDANCE",
            f"{filtered['attendance_rate'].mean():.1f}%"
            if not filtered.empty else "N/A"
        )

    section_title("Performance Records")

    if filtered.empty:

        show_empty_message("No attendees match your search.")

    else:

        st.dataframe(
            filtered[
                [
                    "rank",
                    "attendee_id",
                    "attendee_name",
                    "category",
                    "attendance_rate",
                    "performance_score",
                    "performance_category"
                ]
            ],
            width="stretch",
            hide_index=True
        )

        st.download_button(
            "Download Filtered Performance",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="cci_filtered_performance.csv",
            mime="text/csv"
        )


# ============================================================
# 11. INDIVIDUAL PROFILE
# ============================================================

elif page == "Individual Profile":

    page_header(
        "Individual Attendee Profile",
        "View detailed attendance, engagement and performance information."
    )

    names = sorted(
        df["attendee_name"].dropna().astype(str).unique().tolist()
    )

    if not names:

        show_empty_message("No attendee profiles are available.")

    else:

        selected_name = st.selectbox(
            "Choose an attendee",
            names
        )

        profile = df[
            df["attendee_name"].astype(str) == selected_name
        ].iloc[0]

        st.markdown(
            f"""
            <div class="profile-card">
                <div style="font-size:12px; color:#D0D5DD;">
                    ATTENDEE PROFILE
                </div>
                <h2>{html.escape(str(profile["attendee_name"]))}</h2>
                <p>
                    {html.escape(str(profile["attendee_id"]))}
                    &nbsp; | &nbsp;
                    {html.escape(str(profile["category"]))}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "PERFORMANCE SCORE",
                f'{profile["performance_score"]:.2f}%'
            )

        with c2:
            metric_card("RANKING", f'#{profile["rank"]}')

        with c3:
            metric_card("ATTENDANCE", f'{profile["attendance_rate"]:.1f}%')

        section_title("Performance Breakdown")

        breakdown = pd.DataFrame({
            "Performance Area": [
                "Attendance",
                "Session Participation",
                "Practical Engagement",
                "Teamwork",
                "Activities Completed",
                "Feedback"
            ],
            "Score": [
                profile["attendance_rate"],
                profile["session_participation"] * 10,
                profile["practical_engagement"] * 10,
                profile["teamwork"] * 10,
                profile["activities_completed"],
                profile["feedback_score"] * 10
            ]
        })

        st.bar_chart(
            breakdown,
            x="Performance Area",
            y="Score",
            color=RED
        )

        section_title("Performance Details")

        for _, item in breakdown.iterrows():

            st.markdown(f"**{item['Performance Area']}**")

            st.progress(
                max(0.0, min(1.0, float(item["Score"]) / 100))
            )

            st.caption(f"{item['Score']:.1f}%")


# ============================================================
# 12. PERFORMANCE ANALYTICS
# ============================================================

elif page == "Performance Analytics":

    page_header(
        "Performance Analytics",
        "Understand performance trends and compare attendee groups."
    )

    col1, col2 = st.columns(2)

    with col1:

        section_title("Performance by Category")

        category_data = (
            df["performance_category"]
            .value_counts()
            .rename_axis("Category")
            .reset_index(name="Attendees")
        )

        st.bar_chart(
            category_data,
            x="Category",
            y="Attendees",
            color=RED
        )

    with col2:

        section_title("Average Performance by Group")

        averages = (
            df.groupby("category")["performance_score"]
            .mean()
            .round(2)
            .reset_index()
        )

        averages.columns = ["Attendee Category", "Average Score"]

        st.bar_chart(
            averages,
            x="Attendee Category",
            y="Average Score",
            color=BLUE
        )

    section_title("Performance Summary")

    summary = (
        df.groupby("performance_category")
        .agg(
            attendee_count=("attendee_id", "count"),
            average_score=("performance_score", "mean")
        )
        .round(2)
        .reset_index()
    )

    st.dataframe(
        summary,
        width="stretch",
        hide_index=True
    )

    section_title("Score Statistics")

    st.dataframe(
        df["performance_score"].describe().to_frame("Performance Score"),
        width="stretch"
    )


# ============================================================
# 13. PROGRAMME INSIGHTS
# ============================================================

elif page == "Programme Insights":

    page_header(
        "Programme Insights",
        "Discover engagement patterns and programme performance."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "AVERAGE ATTENDANCE",
            f"{df['attendance_rate'].mean():.1f}%"
        )

    with c2:
        metric_card(
            "PRACTICAL ENGAGEMENT",
            f"{df['practical_engagement'].mean():.1f}/10"
        )

    with c3:
        metric_card(
            "AVERAGE TEAMWORK",
            f"{df['teamwork'].mean():.1f}/10"
        )

    section_title("Attendance and Performance Relationship")

    st.scatter_chart(
        df,
        x="attendance_rate",
        y="performance_score",
        x_label="Attendance Rate (%)",
        y_label="Performance Score (%)",
        color=RED
    )

    section_title("Programme Performance by Attendee Category")

    insights = (
        df.groupby("category")
        .agg(
            attendees=("attendee_id", "count"),
            average_score=("performance_score", "mean"),
            average_attendance=("attendance_rate", "mean")
        )
        .round(2)
        .reset_index()
    )

    insights.columns = [
        "Attendee Category",
        "Attendees",
        "Average Performance",
        "Average Attendance"
    ]

    st.dataframe(
        insights,
        width="stretch",
        hide_index=True
    )

    section_title("Programme Highlights")

    best_attendance = df.loc[df["attendance_rate"].idxmax()]
    best_performance = df.loc[df["performance_score"].idxmax()]

    c1, c2 = st.columns(2)

    with c1:

        st.success(
            f"Highest attendance: {best_attendance['attendee_name']} "
            f"({best_attendance['attendance_rate']:.1f}%)."
        )

    with c2:

        st.success(
            f"Highest performance: {best_performance['attendee_name']} "
            f"({best_performance['performance_score']:.2f}%)."
        )

    st.caption(
        "These are descriptive programme insights. They do not represent "
        "predictions from a trained machine learning model."
    )


# ============================================================
# 14. REPORTS AND DOWNLOADS
# ============================================================

elif page == "Reports & Downloads":

    page_header(
        "Reports & Downloads",
        "Generate and download professional attendee reports."
    )

    section_title("Performance Report")

    st.markdown(
        "Download the complete attendee performance dataset in CSV format."
    )

    st.download_button(
        "Download CSV Report",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="cci_stem_connect_performance.csv",
        mime="text/csv",
        width="stretch"
    )

    section_title("Excel Management Report")

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Attendee Performance",
            index=False
        )

        summary = pd.DataFrame({
            "Metric": [
                "Total Attendees",
                "Average Performance",
                "Highest Performance",
                "Lowest Performance",
                "Average Attendance"
            ],
            "Value": [
                len(df),
                round(df["performance_score"].mean(), 2),
                round(df["performance_score"].max(), 2),
                round(df["performance_score"].min(), 2),
                round(df["attendance_rate"].mean(), 2)
            ]
        })

        summary.to_excel(
            writer,
            sheet_name="Event Summary",
            index=False
        )

        distribution = (
            df["performance_category"]
            .value_counts()
            .rename_axis("Performance Category")
            .reset_index(name="Attendee Count")
        )

        distribution.to_excel(
            writer,
            sheet_name="Performance Distribution",
            index=False
        )

    st.download_button(
        "Download Complete Excel Report",
        data=excel_buffer.getvalue(),
        file_name="cci_stem_connect_management_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch"
    )

    section_title("Report Summary")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("ATTENDEES", len(df))

    with c2:
        metric_card(
            "AVERAGE SCORE",
            f"{df['performance_score'].mean():.2f}%"
        )

    with c3:
        metric_card(
            "AVERAGE ATTENDANCE",
            f"{df['attendance_rate'].mean():.1f}%"
        )


# ============================================================
# 15. DATA MANAGEMENT
# ============================================================

elif page == "Data Management":

    page_header(
        "Data Management",
        "Manage and update the attendee information used by the system."
    )

    section_title("Current Dataset")

    st.metric("Total Attendee Records", len(df))

    st.dataframe(
        df,
        width="stretch",
        hide_index=True
    )

    st.divider()

    section_title("Upload New Dataset")

    st.caption(
        "Upload a CSV or Excel file containing the required attendee columns."
    )

    uploaded_file = st.file_uploader(
        "Select an attendee dataset",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:

        try:

            if uploaded_file.name.lower().endswith(".csv"):
                uploaded_data = pd.read_csv(uploaded_file)
            else:
                uploaded_data = pd.read_excel(uploaded_file)

            st.markdown("#### Dataset Preview")

            st.dataframe(
                uploaded_data.head(),
                width="stretch",
                hide_index=True
            )

            missing = [
                column for column in REQUIRED_COLUMNS
                if column not in uploaded_data.columns
            ]

            if missing:

                st.error(
                    "Required columns are missing: "
                    + ", ".join(missing)
                )

            elif st.button("Validate and Load Dataset"):

                try:

                    validated = validate_data(uploaded_data)

                    processed = calculate_performance(validated)

                    st.session_state.active_data = processed
                    st.session_state.data_source = uploaded_file.name

                    st.success("Dataset loaded successfully.")

                    st.rerun()

                except Exception:

                    logger.exception("Uploaded dataset validation failed.")

                    st.error(
                        "The dataset could not be validated. "
                        "Please check the records and try again."
                    )

        except Exception:

            logger.exception("Uploaded file reading failed.")

            st.error(
                "Unable to read this file. Please check the file format."
            )

    st.divider()

    section_title("Restore Original Company Dataset")

    if st.button("Restore Original Dataset"):

        try:

            st.cache_data.clear()

            original = load_company_data()

            st.session_state.active_data = original
            st.session_state.data_source = "Original company dataset"

            st.success("Original dataset restored.")

            st.rerun()

        except Exception:

            logger.exception("Original dataset restoration failed.")

            st.error(
                "Unable to restore the original dataset."
            )


# ============================================================
# 16. FOOTER
# ============================================================

st.divider()

st.markdown(
    f"""
    <div style="
        text-align:center;
        padding:20px;
        color:{GREY};
        font-size:12px;
    ">
        <b style="color:{NAVY}; font-size:14px;">
            CCI STEM CONNECT
        </b>
        <br>
        LEARN · CONNECT · EXCEL
        <br><br>
        Attendance & Performance Management System
    </div>
    """,
    unsafe_allow_html=True
)
