# Scripts/wotc_submission.py
#
# Simulates the WOTC screening workflow:
#
# Real-world process:
#   1. Employee is hired
#   2. Employer batches new hires weekly (every Friday)
#   3. Batch is submitted to CPA firm / state workforce agency
#   4. CPA firm sends back determinations: employee_id + WOTC category (or Not Eligible)
#
# This script simulates steps 2-4:
#   - Identifies new hires not yet submitted
#   - Groups them into weekly Friday batches based on hire_date
#   - Simulates CPA determination for each employee
#
# Output: Datasets/WOTC_Determinations.csv
#
# Schema:
#   employee_id         | FK -> Dataset1.csv
#   hire_date           | Date employee was hired
#   submission_date     | The Friday their batch was submitted
#   wotc_category       | WOTC target group or "Not Eligible"
#   eligible            | True / False

import random
from datetime import date, timedelta
import pandas as pd

# ---------------------------------------------------------------------------
# WOTC Target Groups (IRS-defined categories) with realistic eligibility rates
# ---------------------------------------------------------------------------
WOTC_CATEGORIES = [
    "Not Eligible",
    "Long-Term Unemployment Recipient",        # 6+ months unemployed
    "TANF Recipient",                          # Temporary Assistance for Needy Families
    "Long-Term TANF Recipient",                # 18+ months on TANF
    "SSI Recipient",                           # Supplemental Security Income
    "Veteran - Unemployed",
    "Veteran - Service-Connected Disability",
    "Ex-Felon",
    "Designated Community Resident",           # lives in Empowerment Zone
    "Vocational Rehabilitation Referral",
    "Summer Youth Employee",
]

# Probability weights: most employees are Not Eligible,
# but home care attracts a higher share of WOTC-eligible populations
# (long-term unemployed, TANF recipients, veterans, ex-felons)
CATEGORY_WEIGHTS = [
    0.52,   # Not Eligible
    0.12,   # Long-Term Unemployment
    0.08,   # TANF
    0.04,   # Long-Term TANF
    0.06,   # SSI
    0.04,   # Veteran - Unemployed
    0.03,   # Veteran - Disability
    0.04,   # Ex-Felon
    0.03,   # Designated Community Resident
    0.02,   # Vocational Rehab
    0.02,   # Summer Youth
]


def _next_friday(d: date) -> date:
    """Return the Friday on or after date d."""
    days_ahead = 4 - d.weekday()  # Friday = weekday 4
    if days_ahead < 0:
        days_ahead += 7
    return d + timedelta(days=days_ahead)


def _determine_eligibility(employee_id: int) -> str:
    """Simulate CPA firm determination for a single employee."""
    random.seed(employee_id)  # deterministic per employee so re-runs are consistent
    category = random.choices(WOTC_CATEGORIES, weights=CATEGORY_WEIGHTS, k=1)[0]
    random.seed()             # reset seed so other randomness is unaffected
    return category


def generate_wotc_determinations(
    employees_df: pd.DataFrame,
    existing_df: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Generate WOTC determinations for all employees not yet processed.

    - Groups new hires into weekly Friday batches by hire_date.
    - Simulates a CPA determination for each employee.
    - Appends to existing_df if provided (for incremental daily runs).

    Returns the full updated determinations DataFrame.
    """
    if existing_df is None or existing_df.empty:
        existing_df = pd.DataFrame()
        already_processed = set()
    else:
        already_processed = set(existing_df["employee_id"].tolist())

    emp = employees_df.copy()
    emp["hire_date"] = pd.to_datetime(emp["hire_date"], errors="coerce").dt.date

    # Only process employees not yet submitted
    to_process = emp[
        emp["hire_date"].notna() &
        ~emp["employee_id"].isin(already_processed)
    ].copy()

    if to_process.empty:
        print("No new employees to submit for WOTC screening.")
        return existing_df

    # Assign each employee to the Friday of their hire week
    to_process["submission_date"] = to_process["hire_date"].apply(_next_friday)

    new_rows = []
    for _, row in to_process.iterrows():
        category = _determine_eligibility(row["employee_id"])
        new_rows.append({
            "employee_id":      row["employee_id"],
            "hire_date":        row["hire_date"],
            "submission_date":  row["submission_date"],
            "wotc_category":    category,
            "eligible":         category != "Not Eligible",
        })

    new_df = pd.DataFrame(new_rows).sort_values(
        ["submission_date", "employee_id"]
    ).reset_index(drop=True)

    # Group summary
    batches = new_df.groupby("submission_date").size()
    for friday, count in batches.items():
        eligible = new_df[new_df["submission_date"] == friday]["eligible"].sum()
        print(f"  Batch {friday} (Friday): {count} employees submitted, "
              f"{eligible} eligible ({eligible/count*100:.0f}%)")

    result = pd.concat([existing_df, new_df], ignore_index=True) if not existing_df.empty else new_df
    print(f"\nTotal: {len(new_df)} new determinations. "
          f"{new_df['eligible'].sum()} eligible "
          f"({new_df['eligible'].mean()*100:.1f}% eligibility rate).")
    return result
