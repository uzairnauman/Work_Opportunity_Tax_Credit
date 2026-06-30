# Scripts/generate_shifts.py
#
# Standalone shift-generation engine.
#
# This deliberately does NOT live inside simulate_day.py. The HR pipeline
# (hire/fire/appraisals) and the scheduling pipeline (clients/shifts) are
# two different systems that happen to share employee_id as a foreign key.
# Keeping them separate means a bug or schema change in one never breaks
# the other, and either can be re-run independently.
#
# Foreign keys:
#   Shifts.employee_id -> Employees.employee_id   (Dataset1.csv)
#   Shifts.client_id    -> Clients.client_id        (Clients.csv)

import random
from datetime import date, datetime, timedelta
import pandas as pd

from .constants import (
    SHIFT_STATUSES,
    SHIFT_STATUS_WEIGHTS,
    SHIFT_START_TIMES,
    SHIFT_LENGTH_HOURS_OPTIONS,
)


def _eligible_employees(employees_df: pd.DataFrame, shift_date: date) -> pd.DataFrame:
    """
    Employees eligible to work on shift_date.

    Important: Dataset1.csv only stores each employee's CURRENT status —
    it has no day-by-day history. So "status == Active" alone is only
    correct for generating *today's* shifts. For backfilling past dates
    (e.g. via backfill_shifts.py looping over many days) we additionally
    require:
      - hire_date <= shift_date   (employee existed yet)
      - terminated_date is null OR terminated_date > shift_date
        (employee hadn't been terminated yet as of this date)

    This means a currently-terminated employee can still correctly show
    up in shifts generated for dates before their terminated_date, and an
    employee hired after shift_date is correctly excluded even though
    they may be "Active" today.
    """
    df = employees_df.copy()
    df["hire_date"] = pd.to_datetime(df["hire_date"], errors="coerce").dt.date
    df["terminated_date"] = pd.to_datetime(df["terminated_date"], errors="coerce").dt.date

    hired_in_time = df["hire_date"].notna() & (df["hire_date"] <= shift_date)
    not_yet_terminated = df["terminated_date"].isna() | (df["terminated_date"] > shift_date)

    return df[hired_in_time & not_yet_terminated]


def _eligible_clients(clients_df: pd.DataFrame) -> pd.DataFrame:
    """Active clients only (Active - On Hold are excluded, they don't get shifts)."""
    return clients_df[clients_df["status"] == "Active"]


def generate_shifts_for_day(
    employees_df: pd.DataFrame,
    clients_df: pd.DataFrame,
    shifts_df: pd.DataFrame,
    shift_date: date = None,
    max_shifts_per_employee: int = 1,
) -> pd.DataFrame:
    """
    Generate one day's worth of shifts.

    Matching logic:
    - Only Active clients get shifts; only Active employees can be assigned.
    - We prefer matching employee.position == client.required_position,
      falling back to any active employee if no position match exists,
      so generation never silently produces zero shifts.
    - Each employee gets at most `max_shifts_per_employee` shifts per day.

    Returns the updated shifts_df (new rows appended).
    """
    if shift_date is None:
        shift_date = date.today()

    active_employees = _eligible_employees(employees_df, shift_date)
    active_clients = _eligible_clients(clients_df)

    if active_employees.empty or active_clients.empty:
        print(f"[{shift_date}] No shifts generated: need at least 1 active employee and 1 active client.")
        return shifts_df

    if shifts_df.empty:
        next_id = 1
    else:
        next_id = int(shifts_df["shift_id"].max()) + 1

    employee_shift_count = {emp_id: 0 for emp_id in active_employees["employee_id"]}
    new_rows = []

    # Each active client may or may not need a shift today (not every client
    # needs one every single day in real life, so roll a chance based on
    # their weekly authorized hours).
    clients_today = active_clients.sample(frac=1).reset_index(drop=True)

    for _, client in clients_today.iterrows():
        # Roughly translate weekly_authorized_hours into a chance of needing
        # a shift on any given day (assume a 7-day week ceiling).
        daily_chance = min(client["weekly_authorized_hours"] / 28, 0.95)
        if random.random() > daily_chance:
            continue

        candidates = active_employees[
            (active_employees["position"] == client["required_position"])
            & (active_employees["employee_id"].map(lambda e: employee_shift_count.get(e, 0)) < max_shifts_per_employee)
        ]

        if candidates.empty:
            # fall back to any available active employee
            candidates = active_employees[
                active_employees["employee_id"].map(lambda e: employee_shift_count.get(e, 0)) < max_shifts_per_employee
            ]

        if candidates.empty:
            continue  # everyone is already booked today

        employee = candidates.sample(n=1).iloc[0]
        employee_shift_count[employee["employee_id"]] += 1

        start_str = random.choice(SHIFT_START_TIMES)
        length_hours = random.choice(SHIFT_LENGTH_HOURS_OPTIONS)
        start_dt = datetime.combine(shift_date, datetime.strptime(start_str, "%H:%M").time())
        end_dt = start_dt + timedelta(hours=length_hours)

        status = random.choices(SHIFT_STATUSES, weights=SHIFT_STATUS_WEIGHTS, k=1)[0]

        if status == "Completed":
            clock_in = start_dt
            clock_out = end_dt
            actual_hours = length_hours
        elif status == "Scheduled":
            clock_in = None
            clock_out = None
            actual_hours = None
        else:
            # Cancelled - Client / Cancelled - Employee / No-Show
            clock_in = None
            clock_out = None
            actual_hours = 0

        shift = {
            "shift_id": next_id + len(new_rows),
            "employee_id": employee["employee_id"],
            "client_id": client["client_id"],
            "shift_date": shift_date,
            "scheduled_start": start_dt,
            "scheduled_end": end_dt,
            "scheduled_hours": length_hours,
            "clock_in": clock_in,
            "clock_out": clock_out,
            "actual_hours": actual_hours,
            "status": status,
            "created_at": date.today(),
        }
        new_rows.append(shift)

    if not new_rows:
        print(f"[{shift_date}] No shifts generated today (no client/employee matches).")
        return shifts_df

    new_shifts_df = pd.DataFrame(new_rows)
    print(f"[{shift_date}] Generated {len(new_rows)} shifts.")
    return pd.concat([shifts_df, new_shifts_df], ignore_index=True)