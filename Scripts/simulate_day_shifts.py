# Scripts/simulate_day_shifts.py
#
# Orchestrator for the SCHEDULING system (Clients + Shifts).
# Mirrors the shape of simulate_day.py (which orchestrates the HR system),
# but is a fully separate pipeline. It reads employees_df read-only to know
# who is Active and eligible for shifts -- it never writes to it.

from datetime import date
import pandas as pd

from .clients import add_clients, discharge_clients
from .generate_shifts import generate_shifts_for_day


def simulate_day_shifts(
    employees_df: pd.DataFrame,
    clients_df: pd.DataFrame,
    shifts_df: pd.DataFrame,
    shift_date: date = None,
    max_new_clients: int = 2,
    max_discharge: int = 1,
):
    """
    Simulate one day of the scheduling system:
    - Randomly onboard 0-max_new_clients new clients
    - Randomly discharge up to max_discharge active clients
    - Generate shifts for the day based on current active employees/clients

    Returns (clients_df, shifts_df). employees_df is read-only here.
    """
    if shift_date is None:
        shift_date = date.today()

    import random
    n_new_clients = random.randint(0, max_new_clients)

    if n_new_clients > 0:
        old_len = len(clients_df)
        clients_df = add_clients(clients_df, n_new=n_new_clients, as_of=shift_date)
        print(f"--- NEW CLIENTS ---")
        print(f"Onboarded {n_new_clients} new client(s) today:")
        print(clients_df.iloc[old_len:][["client_id", "first_name", "last_name", "status", "start_of_care_date"]])
    else:
        print("No new clients onboarded today.")

    clients_df = discharge_clients(clients_df, max_discharge=max_discharge, as_of=shift_date)

    shifts_df = generate_shifts_for_day(
        employees_df=employees_df,
        clients_df=clients_df,
        shifts_df=shifts_df,
        shift_date=shift_date,
    )

    return clients_df, shifts_df
