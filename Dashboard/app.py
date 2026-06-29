import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="HR Dashboard", layout="wide")

# -----------------------------
# MODERN FONT + CLEAN UI
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, sans-serif;
}

/* TITLE */
h1 {
    font-size: 30px !important;
    font-weight: 700;
    letter-spacing: -0.5px;
}

/* SECTION HEADERS */
h2 {
    font-size: 18px !important;
    font-weight: 600;
}

/* METRICS */
[data-testid="metric-container"] {
    background: #fff;
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}

[data-testid="metric-container"] label {
    font-size: 12px !important;
    color: #666;
}

[data-testid="metric-container"] div {
    font-size: 20px !important;
    font-weight: 700;
}

/* CHART CARD FEEL */
.js-plotly-plot {
    background: white;
    border-radius: 14px;
    padding: 10px;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.title("🏥 Workforce Intelligence Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "Datasets" / "Dataset1.csv"

df = pd.read_csv(file_path)
df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce")

# -----------------------------
# MONTH FEATURE (FIXED ORDER)
# -----------------------------
df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce")

df["month_dt"] = df["hire_date"].dt.to_period("M").dt.to_timestamp()
df["month"] = df["month_dt"].dt.strftime("%b %Y")

# sort properly by datetime (NOT alphabet)
months = (
    df[["month", "month_dt"]]
    .dropna()
    .drop_duplicates()
    .sort_values("month_dt")
)

month_labels = months["month"].tolist()


# -----------------------------
# MODERN BUTTON FILTER (SEGMENTED)
# -----------------------------
selected_month = st.segmented_control(
    "📅 Select Month",
    options=["All"] + month_labels,
    default="All"
)

if selected_month != "All":
    df = df[df["month"] == selected_month]

# -----------------------------
# KPI SECTION
# -----------------------------
active = df[~df["status"].str.contains("Resigned|Not Eligible", na=False)]
resigned = df[df["status"].str.contains("Resigned", na=False)]
terminated = df[df["status"].str.contains("Not Eligible", na=False)]

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Employees", len(df))
c2.metric("Active", len(active))
c3.metric("Resigned", len(resigned))
c4.metric("Terminated", len(terminated))

st.divider()

# -----------------------------
# TWO COLUMNS FOR CHARTS
# -----------------------------
col1, col2 = st.columns(2)

# -----------------------------
# ROLE DISTRIBUTION (HORIZONTAL)
# -----------------------------
role_counts = df["position"].value_counts().reset_index()
role_counts.columns = ["Role", "Employees"]

fig_roles = px.bar(
    role_counts,
    x="Employees",
    y="Role",
    text="Employees",
    orientation="h"
)

fig_roles.update_layout(
    template="simple_white",
    title="Workforce by Role",
    font=dict(family="Inter, system-ui", size=12),
    title_font_size=16,
    margin=dict(l=20, r=20, t=40, b=20)
)

fig_roles.update_traces(
    marker_color="#4F46E5",
    textposition="outside"
)

fig_roles.update_xaxes(showgrid=False)
fig_roles.update_yaxes(showgrid=False)

col1.plotly_chart(fig_roles, use_container_width=True)

# -----------------------------
# AVERAGE PAY (HORIZONTAL)
# -----------------------------
avg_pay = df.groupby("position")["base_pay_rate"].mean().reset_index()
avg_pay.columns = ["Role", "Avg Pay"]

fig_pay = px.bar(
    avg_pay,
    x="Avg Pay",
    y="Role",
    text="Avg Pay",
    orientation="h"
)

fig_pay.update_layout(
    template="simple_white",
    title="Average Pay by Role",
    font=dict(family="Inter, system-ui", size=12),
    title_font_size=16,
    margin=dict(l=20, r=20, t=40, b=20)
)

fig_pay.update_traces(
    marker_color="#10B981",
    textposition="outside"
)

fig_pay.update_xaxes(showgrid=False)
fig_pay.update_yaxes(showgrid=False)

col2.plotly_chart(fig_pay, use_container_width=True)