# main_shifts.py
#
# Entry point for the SCHEDULING system (Clients + Shifts), effective
# 07/01/2026. This is intentionally a separate script from main.py.
#
# main.py        -> runs the HR pipeline  -> writes Datasets/Dataset1.csv
# main_shifts.py -> runs the scheduling pipeline -> writes
#                    Datasets/Clients.csv and Datasets/Shifts.csv
#
# Running one never touches the other's file. Both can be scheduled
# independently (e.g. two separate GitHub Actions jobs).

import os
from datetime import date
import pandas as pd

from Scripts.simulate_day_shifts import simulate_day_shifts

EMPLOYEES_PATH = "Datasets/Dataset1.csv"
CLIENTS_PATH = "Datasets/Clients.csv"
SHIFTS_PATH = "Datasets/Shifts.csv"

SYSTEM_START_DATE = date(2026, 7, 1)


def load_or_empty(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()


def main():
    employees_df = load_or_empty(EMPLOYEES_PATH)
    if employees_df.empty:
        raise SystemExit(
            f"{EMPLOYEES_PATH} not found or empty. The scheduling system "
            "needs the existing employee dataset to know who is Active."
        )

    clients_df = load_or_empty(CLIENTS_PATH)
    shifts_df = load_or_empty(SHIFTS_PATH)

    today = date.today()
    if today < SYSTEM_START_DATE:
        print(
            f"Scheduling system starts {SYSTEM_START_DATE.isoformat()}; "
            f"today is {today.isoformat()}. Nothing to do yet."
        )
        return

    clients_df, shifts_df = simulate_day_shifts(
        employees_df=employees_df,
        clients_df=clients_df,
        shifts_df=shifts_df,
        shift_date=today,
        max_new_clients=3,
        max_discharge=1,
    )

    clients_df.to_csv(CLIENTS_PATH, index=False)
    shifts_df.to_csv(SHIFTS_PATH, index=False)

    print("\n--- Final Clients Data (tail) ---")
    print(clients_df.tail())
    print("\n--- Final Shifts Data (tail) ---")
    print(shifts_df.tail())


if __name__ == "__main__":
    main()
