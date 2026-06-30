from constants import RATINGS, POSITIONS, EDUCATION, LANGUAGES
from hire import hire_employees
from fire_employee import fire_employees


import pandas as pd
import random
from datetime import date

def simulate_day(df, max_hire=4, max_fire=3):
    """
    Simulate one "day" at the company:
    - Randomly hire 1 to max_hire employees
    - Randomly fire up to max_fire active employees
    - Log hires and terminations
    Returns updated DataFrame.
    """
    # --- HIRING ---
    n_hire = random.randint(1, max_hire)
    old_len = len(df)
    df = hire_employees(df, n_new=n_hire)
    new_hires = df.iloc[old_len:]

    print(f"--- HIRING ---")
    print(f"Hired {n_hire} new employees today:")
    print(new_hires[['employee_id', 'first_name', 'last_name', 'status', 'hire_date']])

    # --- FIRING ---
    n_active_before = len(df[df['status'] == "Active"])
    df = fire_employees(df, max_fire=max_fire)
    n_active_after = len(df[df['status'] == "Active"])
    n_fired = n_active_before - n_active_after

    terminated_employees = df[df['terminated_date'] == date.today()]
    if n_fired > 0:
        print(f"\n--- FIRING ---")
        print(f"Fired {n_fired} employees today:")
        print(terminated_employees[['employee_id', 'first_name', 'last_name', 'status', 'terminated_date']])
    else:
        print("\nNo employees fired today.")

    return df