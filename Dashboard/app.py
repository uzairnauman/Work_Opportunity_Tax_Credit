import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="HR Dashboard", layout="wide")

# -----------------------------
# PREMIUM NOISE-FREE STYLES
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global Reset for Clean Typography matching chat style */
html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    color: #1F2937;
}

/* Header styling */
h1 { font-size: 28px !important; font-weight: 700 !important; letter-spacing: -0.6px !important; color: #111827; margin-bottom: 24px !important; }
h2 { font-size: 20px !important; font-weight: 600 !important; letter-spacing: -0.4px !important; color: #111827; }
h4 { font-size: 16px !important; font-weight: 600 !important; color: #374151; margin-top: 12px !important; }

/* Modern Minimalist Metric Cards */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}
[data-testid="metric-container"] label { font-size: 13px !important; font-weight: 500 !important; color: #6B7280 !important; }
[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; color: #111827 !important; }

/* Noise reduction on standard dividers */
hr { margin: 2rem 0 !important; border-color: #F3F4F6 !important; }

/* Clean UI Dataframes */
[data-testid="stTable"], [data-testid="stDataFrame"] {
    border-radius: 8px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

st.title("HR Dashboard — Home Care Business")

# Custom Modern Palette
MODERN_PALETTE = ["#4F46E5", "#0D9488", "#F59E0B", "#EF4444", "#10B981", "#6366F1"]

# -----------------------------
# LOAD DATA
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

employees_df = pd.read_csv(BASE_DIR / "Datasets" / "Dataset1.csv")
employees_df["hire_date"] = pd.to_datetime(employees_df["hire_date"], errors="coerce")

shifts_exists = (BASE_DIR / "Datasets" / "Shifts.csv").exists()
clients_exists = (BASE_DIR / "Datasets" / "Clients.csv").exists()

if shifts_exists:
    shifts_df  = pd.read_csv(BASE_DIR / "Datasets" / "Shifts.csv", parse_dates=["shift_date"])
if clients_exists:
    clients_df = pd.read_csv(BASE_DIR / "Datasets" / "Clients.csv")

# -----------------------------
# TABS
# -----------------------------
wotc_exists = (BASE_DIR / "Datasets" / "WOTC_Determinations.csv").exists()
if wotc_exists:
    wotc_df = pd.read_csv(BASE_DIR / "Datasets" / "WOTC_Determinations.csv")

tab_hr, tab_shifts, tab_wotc = st.tabs(["HR Overview", "Shifts Scoreboard", "WOTC Tracking"])


# ============================================================
# TAB 1 — HR OVERVIEW
# ============================================================
with tab_hr:

    employees_df["month_dt"] = employees_df["hire_date"].dt.to_period("M").dt.to_timestamp()
    employees_df["month"]    = employees_df["month_dt"].dt.strftime("%b %Y")
    month_labels = (
        employees_df[["month", "month_dt"]]
        .dropna().drop_duplicates().sort_values("month_dt")["month"].tolist()
    )

    selected_month = st.segmented_control(
        "Filter by Hire Month",
        options=["All"] + month_labels,
        default="All"
    )

    df = employees_df.copy()
    if selected_month != "All":
        df = df[df["month"] == selected_month]

    active     = df[~df["status"].str.contains("Resigned|Not Eligible", na=False)]
    resigned   = df[df["status"].str.contains("Resigned", na=False)]
    terminated = df[df["status"].str.contains("Not Eligible", na=False)]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Employees", len(df))
    c2.metric("Active",          len(active))
    c3.metric("Resigned",        len(resigned))
    c4.metric("Terminated",      len(terminated))

    st.divider()

    col1, col2 = st.columns(2)

    # Role distribution
    role_counts = df["position"].value_counts().reset_index()
    role_counts.columns = ["Role", "Employees"]
    fig_roles = px.bar(role_counts, x="Employees", y="Role", text="Employees", orientation="h")
    fig_roles.update_layout(
        template="simple_white", 
        title="Workforce by Role",
        font=dict(family="Inter, system-ui", size=14, color="#1F2937"),
        title_font=dict(size=16, weight="bold", color="#111827"),
        margin=dict(l=120, r=40, t=50, b=10),
        showlegend=False
    )
    fig_roles.update_traces(marker_color="#4F46E5", textposition="outside", marker_line_width=0, width=0.5)
    fig_roles.update_xaxes(showgrid=False, visible=False)
    fig_roles.update_yaxes(showgrid=False, zeroline=False, type='category', tickfont=dict(size=14))
    col1.plotly_chart(fig_roles, use_container_width=True, config={'displayModeBar': False})

    # Average pay
    avg_pay = df.groupby("position")["base_pay_rate"].mean().reset_index()
    avg_pay.columns = ["Role", "Avg Pay"]
    fig_pay = px.bar(avg_pay, x="Avg Pay", y="Role", text="Avg Pay", orientation="h")
    fig_pay.update_layout(
        template="simple_white", 
        title="Average Pay by Role",
        font=dict(family="Inter, system-ui", size=14, color="#1F2937"),
        title_font=dict(size=16, weight="bold", color="#111827"),
        margin=dict(l=120, r=40, t=50, b=10),
        showlegend=False
    )
    fig_pay.update_traces(marker_color="#0D9488", textposition="outside", texttemplate="$%{text:.2f}", marker_line_width=0, width=0.5)
    fig_pay.update_xaxes(showgrid=False, visible=False)
    fig_pay.update_yaxes(showgrid=False, zeroline=False, type='category', tickfont=dict(size=14))
    col2.plotly_chart(fig_pay, use_container_width=True, config={'displayModeBar': False})


# ============================================================
# TAB 2 — SHIFTS SCOREBOARD
# ============================================================
with tab_shifts:

    if not shifts_exists:
        st.info("No Shifts data found yet. Run `backfill_shifts.py` or `main_shifts.py` first.")
        st.stop()

    st.markdown("#### Filter Period")
    fcol1, fcol2 = st.columns([1, 3])

    with fcol1:
        granularity = st.segmented_control(
            "Granularity",
            options=["Week", "Month", "All Time"],
            default="Week"
        )

    with fcol2:
        s = shifts_df.copy()
        s["year_week"]  = s["shift_date"].dt.strftime("W%W · %Y")
        s["year_month"] = s["shift_date"].dt.strftime("%b %Y")

        week_options = (
            s[["year_week", "shift_date"]].drop_duplicates()
            .sort_values("shift_date")["year_week"].unique().tolist()
        )
        month_options = (
            s[["year_month", "shift_date"]].assign(
                m=s["shift_date"].dt.to_period("M").dt.to_timestamp()
            ).drop_duplicates(subset=["year_month"])
            .sort_values("m")["year_month"].unique().tolist()
        )

        if granularity == "Week":
            selected_period = st.segmented_control(
                "Select Week", options=week_options, default=week_options[-1]
            )
            s = s[s["year_week"] == selected_period]
            period_label = selected_period

        elif granularity == "Month":
            selected_period = st.segmented_control(
                "Select Month", options=month_options, default=month_options[-1]
            )
            s = s[s["year_month"] == selected_period]
            period_label = selected_period

        else:
            period_label = "All Time"

    selected_statuses = st.multiselect(
        "Shift Status",
        options=sorted(shifts_df["status"].unique().tolist()),
        default=["Completed"],
        help="Completed = hours actually worked."
    )
    if selected_statuses:
        s = s[s["status"].isin(selected_statuses)]

    st.divider()

    merged = s.merge(
        employees_df[["employee_id", "first_name", "last_name", "position"]],
        on="employee_id",
        how="left"
    )
    merged["employee"] = merged["first_name"] + " " + merged["last_name"]

    total_shifts    = len(s)
    total_hours     = s["actual_hours"].fillna(0).sum()
    unique_employees = s["employee_id"].nunique()
    completion_rate = (len(s[s["status"] == "Completed"]) / len(s) * 100 if len(s) > 0 else 0)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Shifts",             f"{total_shifts:,}")
    k2.metric("Hours Worked",       f"{total_hours:,.0f} hrs")
    k3.metric("Employees Scheduled",f"{unique_employees}")
    k4.metric("Completion Rate",    f"{completion_rate:.1f}%")

    st.divider()

    scoreboard = (
        merged.groupby(["employee_id", "employee", "position"])
        .agg(
            shifts=("shift_id", "count"),
            hours=("actual_hours", lambda x: x.fillna(0).sum()),
            completed=("status", lambda x: (x == "Completed").sum()),
        )
        .reset_index()
        .sort_values("hours", ascending=False)
        .reset_index(drop=True)
    )
    scoreboard.index += 1

    board_col, chart_col = st.columns([1, 2])

    with board_col:
        st.markdown(f"**Employee Hours · {period_label}**")
        display = scoreboard[["employee", "position", "shifts", "hours", "completed"]].copy()
        display.columns = ["Employee", "Position", "Shifts", "Hours", "Completed"]
        display["Hours"] = display["Hours"].map(lambda x: f"{x:.0f}")
        st.dataframe(display, use_container_width=True, height=440)

    with chart_col:
        # Row layout row limit control
        max_rows_scoreboard = st.slider("Rows to Display", min_value=5, max_value=30, value=15, key="sb_slider")
        top_n = scoreboard.head(max_rows_scoreboard)
        fig = px.bar(
            top_n, x="hours", y="employee", color="position", orientation="h", text="hours",
            title=f"Hours Worked by Employee (Top {max_rows_scoreboard})",
            labels={"hours": "Hours Worked", "employee": "", "position": "Position"},
            color_discrete_sequence=MODERN_PALETTE
        )
        fig.update_layout(
            template="simple_white",
            font=dict(family="Inter, system-ui", size=14, color="#1F2937"),
            title_font=dict(size=16, weight="bold", color="#111827"),
            margin=dict(l=140, r=40, t=60, b=80),
            yaxis=dict(autorange="reversed", type='category', tickfont=dict(size=14)),
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0, title=None),
            height=max(350, len(top_n) * 32)
        )
        fig.update_traces(texttemplate="%{text:.0f} hrs", textposition="outside", marker_line_width=0, width=0.5)
        fig.update_xaxes(showgrid=False, visible=False)
        fig.update_yaxes(showgrid=False, zeroline=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.markdown("**Hours by Position**")
    pos_summary = (
        merged[merged["status"] == "Completed"]
        .groupby("position")["actual_hours"].sum().reset_index()
        .sort_values("actual_hours", ascending=False)
    )
    pos_summary.columns = ["Position", "Hours"]

    fig_pos = px.bar(
        pos_summary, x="Position", y="Hours", text="Hours",
        color="Position", color_discrete_sequence=MODERN_PALETTE
    )
    fig_pos.update_layout(
        template="simple_white",
        font=dict(family="Inter, system-ui", size=14, color="#1F2937"),
        showlegend=False,
        margin=dict(l=10, r=10, t=30, b=10),
        height=280
    )
    fig_pos.update_traces(texttemplate="%{text:.0f} hrs", textposition="outside", marker_line_width=0, width=0.3)
    fig_pos.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=14))
    fig_pos.update_yaxes(showgrid=False, visible=False)
    st.plotly_chart(fig_pos, use_container_width=True, config={'displayModeBar': False})


# ============================================================
# TAB 3 — WOTC TRACKING
# ============================================================
with tab_wotc:

    if not wotc_exists or not shifts_exists:
        st.info("Missing WOTC data dependencies.")
        st.stop()

    active_employees = employees_df[employees_df["status"] == "Active"][
        ["employee_id", "first_name", "last_name", "position", "base_pay_rate"]
    ].copy()

    eligible_active = wotc_df[wotc_df["eligible"] == True].merge(active_employees, on="employee_id", how="inner")

    completed_hours = (
        shifts_df[shifts_df["status"] == "Completed"]
        .groupby("employee_id")["actual_hours"].sum()
        .reset_index().rename(columns={"actual_hours": "total_hours"})
    )

    tracking = eligible_active.merge(completed_hours, on="employee_id", how="left")
    tracking["total_hours"] = tracking["total_hours"].fillna(0)
    tracking["employee"]    = tracking["first_name"] + " " + tracking["last_name"]
    tracking["hours_remaining_120"] = (120 - tracking["total_hours"]).clip(lower=0)
    tracking["hours_remaining_400"] = (400 - tracking["total_hours"]).clip(lower=0)

    under_120  = tracking[tracking["total_hours"] < 120].sort_values("total_hours", ascending=False)
    mid_range  = tracking[(tracking["total_hours"] >= 120) & (tracking["total_hours"] < 400)].sort_values("total_hours", ascending=False)
    maxed_out  = tracking[tracking["total_hours"] >= 400]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Eligible Active Employees", len(tracking))
    k2.metric("Under 120 hrs",            len(under_120), help="No credit earned yet")
    k3.metric("120–399 hrs",              len(mid_range), help="Partial credit")
    k4.metric("400+ hrs",                 len(maxed_out), help="Full credit")

    st.divider()

    # Shared slider configuration tool for dynamic layout control
    max_rows_wotc = st.slider("Maximum Employees to Display", min_value=5, max_value=30, value=12, key="wotc_slider")

    st.markdown("#### At Risk — Under 120 Hours (No Credit Yet)")
    st.caption("These employees are WOTC eligible but haven't worked enough hours to earn any credit. Prioritize scheduling them.")

    if under_120.empty:
        st.success("All eligible employees have cleared 120 hours.")
    else:
        top_under_120 = under_120.head(max_rows_wotc)
        fig1 = px.bar(
            top_under_120, x="total_hours", y="employee", color="wotc_category", orientation="h", text="total_hours",
            labels={"total_hours": "Hours Worked", "employee": "", "wotc_category": "WOTC Category"},
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig1.add_vline(x=120, line_dash="dash", line_color="#4B5563", annotation_text="120 hr minimum", annotation_position="top right")
        fig1.update_layout(
            template="simple_white",
            font=dict(family="Inter, system-ui", size=14, color="#1F2937"),
            margin=dict(l=140, r=40, t=50, b=100),
            yaxis=dict(autorange="reversed", type='category', tickfont=dict(size=14)),
            height=max(350, len(top_under_120) * 32),
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0, title=None),
        )
        fig1.update_traces(texttemplate="%{text:.0f} hrs", textposition="outside", marker_line_width=0, width=0.5)
        fig1.update_xaxes(showgrid=False, range=[0, 140], visible=False)
        fig1.update_yaxes(showgrid=False, zeroline=False)
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    st.markdown("#### In Progress — 120 to 399 Hours (Partial Credit)")
    st.caption("These employees have earned partial credit. Getting them to 400 hours unlocks the full credit amount.")

    if mid_range.empty:
        st.info("No eligible employees in the 120–399 hour range yet.")
    else:
        top_mid_range = mid_range.head(max_rows_wotc)
        fig2 = px.bar(
            top_mid_range, x="total_hours", y="employee", color="wotc_category", orientation="h", text="total_hours",
            labels={"total_hours": "Hours Worked", "employee": "", "wotc_category": "WOTC Category"},
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig2.add_vline(x=400, line_dash="dash", line_color="#0D9488", annotation_text="400 hr full credit", annotation_position="top right")
        fig2.update_layout(
            template="simple_white",
            font=dict(family="Inter, system-ui", size=14, color="#1F2937"),
            margin=dict(l=140, r=40, t=50, b=100),
            yaxis=dict(autorange="reversed", type='category', tickfont=dict(size=14)),
            height=max(350, len(top_mid_range) * 32),
            legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="left", x=0, title=None),
        )
        fig2.update_traces(texttemplate="%{text:.0f} hrs", textposition="outside", marker_line_width=0, width=0.5)
        fig2.update_xaxes(showgrid=False, range=[0, 440], visible=False)
        fig2.update_yaxes(showgrid=False, zeroline=False)
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    st.divider()
    
    # ----------------------------------------------------------
    # REWRITTEN: WOTC CATEGORY BREAKDOWN VISUALIZATION
    # ----------------------------------------------------------
    st.markdown("#### Eligible Employees by WOTC Category")
    cat_summary = (
        tracking.groupby("wotc_category")
        .agg(employees=("employee_id", "count"), avg_hours=("total_hours", "mean"))
        .reset_index().sort_values("employees", ascending=False)
    )
    cat_summary.columns = ["WOTC Category", "Employees", "Avg Hours"]
    
    fig_cat = px.bar(
        cat_summary, x="Employees", y="WOTC Category", orientation="h", text="Employees",
        color="WOTC Category", color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_cat.update_layout(
        template="simple_white",
        font=dict(family="Inter, system-ui", size=14, color="#1F2937"),
        showlegend=False,
        margin=dict(l=240, r=40, t=20, b=20),
        height=max(280, len(cat_summary) * 35),
        yaxis=dict(autorange="reversed", type='category', tickfont=dict(size=14))
    )
    fig_cat.update_traces(textposition="outside", marker_line_width=0, width=0.5)
    fig_cat.update_xaxes(showgrid=False, visible=False)
    fig_cat.update_yaxes(showgrid=False, zeroline=False)
    st.plotly_chart(fig_cat, use_container_width=True, config={'displayModeBar': False})