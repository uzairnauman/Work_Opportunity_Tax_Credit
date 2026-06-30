# backfill_shifts.py
#
# One-time / on-demand seed script for the new scheduling system.
#
# main_shifts.py is meant to run once per day going forward (via GitHub
# Actions, same pattern as main.py). But the new system officially starts
# 07/01/2026, and we want a dataset that already has some history in it
# instead of starting from a single empty day. This script walks day-by-day
# from SYSTEM_START_DATE up to --end-date (default: today) and builds
# Clients.csv / Shifts.csv exactly the way main_shifts.py would have, one
# day at a time, so the result is indistinguishable from "the daily job had
# been running since 07/01/2026."
#
# Run this once to seed history, then let main_shifts.py take over daily.
# Re-running it is safe to do for a fresh dataset, but it does NOT append --
# it always rebuilds Clients.csv/Shifts.csv from SYSTEM_START_DATE forward.

import argparse
import os
from datetime import date, timedelta
import pandas as pd

from Scripts.simulate_day_shifts import simulate_day_shifts

EMPLOYEES_PATH = "Datasets/Dataset1.csv"
CLIENTS_PATH = "Datasets/Clients.csv"
SHIFTS_PATH = "Datasets/Shifts.csv"

SYSTEM_START_DATE = date(2026, 7, 1)

# How many clients to onboard on day 1 so there's a real client base
# before shifts start generating, rather than growing from zero.
INITIAL_CLIENT_SEED = 25


def parse_args():
    p = argparse.ArgumentParser(description="Backfill Clients/Shifts history from 07/01/2026.")
    p.add_argument(
        "--end-date",
        type=str,
        default=date.today().isoformat(),
        help="Last day to simulate (YYYY-MM-DD). Defaults to today.",
    )
    return p.parse_args()


def main():
    args = parse_args()
    end_date = date.fromisoformat(args.end_date)

    if end_date < SYSTEM_START_DATE:
        raise SystemExit(
            f"--end-date {end_date} is before the system start date {SYSTEM_START_DATE}."
        )

    if not os.path.exists(EMPLOYEES_PATH):
        raise SystemExit(f"{EMPLOYEES_PATH} not found. Run main.py first to seed employees.")

    employees_df = pd.read_csv(EMPLOYEES_PATH)

    clients_df = pd.DataFrame()
    shifts_df = pd.DataFrame()

    from Scripts.clients import add_clients
    clients_df = add_clients(clients_df, n_new=INITIAL_CLIENT_SEED, as_of=SYSTEM_START_DATE)
    print(f"Seeded {INITIAL_CLIENT_SEED} clients as of {SYSTEM_START_DATE.isoformat()}.")

    current = SYSTEM_START_DATE
    while current <= end_date:
        clients_df, shifts_df = simulate_day_shifts(
            employees_df=employees_df,
            clients_df=clients_df,
            shifts_df=shifts_df,
            shift_date=current,
            max_new_clients=3,
            max_discharge=1,
        )
        current += timedelta(days=1)

    clients_df.to_csv(CLIENTS_PATH, index=False)
    shifts_df.to_csv(SHIFTS_PATH, index=False)

    print(f"\nDone. {len(clients_df)} clients, {len(shifts_df)} shifts written.")
    print(f"  {CLIENTS_PATH}")
    print(f"  {SHIFTS_PATH}")


if __name__ == "__main__":
    main()
