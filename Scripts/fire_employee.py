from datetime import date
from .constants import TERMINATION_STATUSES
import random

TERMINATION_STATUSES = [
    "Resigned/Separated - Eligible for Rehire",
    "Resigned/Separated - Not Eligible for Rehire"
]

def fire_employees(df, max_fire=3):
    """
    Randomly terminate up to `max_fire` active employees.
    Returns updated DataFrame.
    """
    # Filter active employees eligible for termination
    active_employees = df[df['status'] == "Active"]

    if active_employees.empty:
        print("No active employees to fire today.")
        return df

    # Number to fire: random up to max_fire or number of active employees
    n_fire = random.randint(1, min(max_fire, len(active_employees)))

    # Randomly select employees to fire
    employees_to_fire = active_employees.sample(n=n_fire, random_state=random.randint(0, 9999))

    # Update their status and terminated_date
    for idx in employees_to_fire.index:
        # Decide termination type
        status = random.choices(
            TERMINATION_STATUSES, weights=[0.7, 0.3], k=1
        )[0]

        df.at[idx, 'status'] = status
        df.at[idx, 'terminated_date'] = date.today()

    print(f"Fired {n_fire} employees today.")
    return df


