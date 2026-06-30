import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="HR Dashboard", layout="wide")

# -----------------------------
# SHARED STYLES
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, sans-serif;
}
h1 { font-size: 30px !important; font-weight: 700; letter-spacing: -0.5px; }
h2 { font-size: 18px !important; font-weight: 600; }

[data-testid="metric-container"] {
    background: #fff;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
[data-testid="metric-container"] label { font-size: 12px !important; color: #666; }
[data-testid="metric-container"] div  { font-size: 20px !important; font-weight: 700; }

.js-plotly-plot {
    background: white;
    border-radius: 14px;
    padding: 10px;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

st.title("HR Dashboard — Home Care Business")

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
tab_hr, tab_shifts = st.tabs(["👥 HR Overview", "📋 Shifts Scoreboard"])


# ============================================================
# TAB 1 — HR OVERVIEW  (existing content, unchanged)
# ============================================================
with tab_hr:

    # Month filter (existing logic)
    employees_df["month_dt"] = employees_df["hire_date"].dt.to_period("M").dt.to_timestamp()
    employees_df["month"]    = employees_df["month_dt"].dt.strftime("%b %Y")
    month_labels = (
        employees_df[["month", "month_dt"]]
        .dropna().drop_duplicates().sort_values("month_dt")["month"].tolist()
    )

    selected_month = st.segmented_control(
        "📅 Filter by Hire Month",
        options=["All"] + month_labels,
        default="All"
    )

    df = employees_df.copy()
    if selected_month != "All":
        df = df[df["month"] == selected_month]

    # KPIs
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
    fig_roles.update_layout(template="simple_white", title="Workforce by Role",
                            font=dict(family="Inter, system-ui", size=12),
                            title_font_size=16, margin=dict(l=20, r=20, t=40, b=20))
    fig_roles.update_traces(marker_color="#4F46E5", textposition="outside")
    fig_roles.update_xaxes(showgrid=False)
    fig_roles.update_yaxes(showgrid=False)
    col1.plotly_chart(fig_roles, use_container_width=True)

    # Average pay
    avg_pay = df.groupby("position")["base_pay_rate"].mean().reset_index()
    avg_pay.columns = ["Role", "Avg Pay"]
    fig_pay = px.bar(avg_pay, x="Avg Pay", y="Role", text="Avg Pay", orientation="h")
    fig_pay.update_layout(template="simple_white", title="Average Pay by Role",
                          font=dict(family="Inter, system-ui", size=12),
                          title_font_size=16, margin=dict(l=20, r=20, t=40, b=20))
    fig_pay.update_traces(marker_color="#10B981", textposition="outside")
    fig_pay.update_xaxes(showgrid=False)
    fig_pay.update_yaxes(showgrid=False)
    col2.plotly_chart(fig_pay, use_container_width=True)


# ============================================================
# TAB 2 — SHIFTS SCOREBOARD
# ============================================================
with tab_shifts:

    if not shifts_exists:
        st.info("No Shifts data found yet. Run `backfill_shifts.py` or `main_shifts.py` first.")
        st.stop()

    # ----------------------------------------------------------
    # PERIOD FILTER  (granularity first, then specific period)
    # ----------------------------------------------------------
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
        s["year_week"]  = s["shift_date"].dt.strftime("W%W · %Y")   # e.g. W27 · 2026
        s["year_month"] = s["shift_date"].dt.strftime("%b %Y")       # e.g. Jul 2026

        # Build sorted option lists
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

        else:  # All Time
            period_label = "All Time"

    # ----------------------------------------------------------
    # STATUS FILTER  (only show Completed by default but allow expanding)
    # ----------------------------------------------------------
    status_options = sorted(shifts_df["status"].unique().tolist())
    selected_statuses = st.multiselect(
        "Shift Status",
        options=status_options,
        default=["Completed"],
        help="Completed = hours actually worked. Include Cancelled/No-Show to see full scheduling picture."
    )
    if selected_statuses:
        s = s[s["status"].isin(selected_statuses)]

    st.divider()

    # ----------------------------------------------------------
    # JOIN TO EMPLOYEES for name + position
    # ----------------------------------------------------------
    merged = s.merge(
        employees_df[["employee_id", "first_name", "last_name", "position"]],
        on="employee_id",
        how="left"
    )
    merged["employee"] = merged["first_name"] + " " + merged["last_name"]

    # ----------------------------------------------------------
    # KPIs
    # ----------------------------------------------------------
    total_shifts    = len(s)
    total_hours     = s["actual_hours"].fillna(0).sum()
    unique_employees = s["employee_id"].nunique()
    completion_rate = (
        len(s[s["status"] == "Completed"]) / len(s) * 100
        if len(s) > 0 else 0
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Shifts",             f"{total_shifts:,}")
    k2.metric("Hours Worked",       f"{total_hours:,.0f} hrs")
    k3.metric("Employees Scheduled",f"{unique_employees}")
    k4.metric("Completion Rate",    f"{completion_rate:.1f}%")

    st.divider()

    # ----------------------------------------------------------
    # SCOREBOARD — hours per employee (bar chart + table)
    # ----------------------------------------------------------
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
    scoreboard.index += 1  # rank starts at 1

    board_col, chart_col = st.columns([1, 2])

    with board_col:
        st.markdown(f"**Employee Hours · {period_label}**")
        display = scoreboard[["employee", "position", "shifts", "hours", "completed"]].copy()
        display.columns = ["Employee", "Position", "Shifts", "Hours", "Completed"]
        display["Hours"] = display["Hours"].map(lambda x: f"{x:.0f}")
        st.dataframe(display, use_container_width=True, height=420)

    with chart_col:
        top_n = scoreboard.head(20)
        fig = px.bar(
            top_n,
            x="hours",
            y="employee",
            color="position",
            orientation="h",
            text="hours",
            title=f"Hours Worked by Employee · {period_label} (Top 20)",
            labels={"hours": "Hours Worked", "employee": "", "position": "Position"}
        )
        fig.update_layout(
            template="simple_white",
            font=dict(family="Inter, system-ui", size=12),
            title_font_size=15,
            margin=dict(l=20, r=20, t=40, b=20),
            yaxis=dict(autorange="reversed"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_traces(texttemplate="%{text:.0f} hrs", textposition="outside")
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------------------
    # POSITION SUMMARY (compact, below)
    # ----------------------------------------------------------
    st.markdown("**Hours by Position**")
    pos_summary = (
        merged[merged["status"] == "Completed"]
        .groupby("position")["actual_hours"]
        .sum().reset_index()
        .sort_values("actual_hours", ascending=False)
    )
    pos_summary.columns = ["Position", "Hours"]

    fig_pos = px.bar(
        pos_summary, x="Position", y="Hours", text="Hours",
        color="Position", color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pos.update_layout(
        template="simple_white",
        font=dict(family="Inter, system-ui", size=12),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        height=280
    )
    fig_pos.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig_pos.update_xaxes(showgrid=False)
    fig_pos.update_yaxes(showgrid=False)
    st.plotly_chart(fig_pos, use_container_width=True)