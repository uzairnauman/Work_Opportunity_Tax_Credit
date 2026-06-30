# main_wotc.py
#
# Entry point for the WOTC screening pipeline.
#
# Three separate pipelines, three separate entrypoints:
#   main.py         -> HR (hire/fire)          -> Dataset1.csv
#   main_shifts.py  -> Scheduling              -> Clients.csv, Shifts.csv
#   main_wotc.py    -> WOTC screening          -> WOTC_Determinations.csv
#
# Run this after main.py has updated Dataset1.csv with new hires.
# It finds any employees not yet screened, groups them into weekly
# Friday batches, and simulates CPA firm determinations.

import os
import pandas as pd
from Scripts.wotc_submission import generate_wotc_determinations

EMPLOYEES_PATH    = "Datasets/Dataset1.csv"
WOTC_PATH         = "Datasets/WOTC_Determinations.csv"


def main():
    if not os.path.exists(EMPLOYEES_PATH):
        raise SystemExit(f"{EMPLOYEES_PATH} not found. Run main.py first.")

    employees_df = pd.read_csv(EMPLOYEES_PATH)

    existing_df = pd.read_csv(WOTC_PATH) if os.path.exists(WOTC_PATH) else pd.DataFrame()

    print("--- WOTC SCREENING ---")
    determinations_df = generate_wotc_determinations(
        employees_df=employees_df,
        existing_df=existing_df,
    )

    determinations_df.to_csv(WOTC_PATH, index=False)
    print(f"\nSaved to {WOTC_PATH}")
    print(determinations_df.tail(10).to_string(index=False))


if __name__ == "__main__":
    main()
