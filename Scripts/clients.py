# Scripts/clients.py
#
# Generates and maintains the Clients dataset (Dataset2).
# This is intentionally separate from the employee/HR system (hire.py,
# fire_employee.py, simulate_day.py) so the two pipelines never collide.
# Clients are who shifts get booked against; employees are who shifts get
# assigned to. Shift generation (generate_shifts.py) reads both but writes
# neither of these files.

from faker import Faker
import random
from datetime import date
import pandas as pd

from .constants import PAYER_TYPES, CARE_TYPES, CLIENT_STATUSES, CLIENT_REQUIRED_POSITIONS

fake = Faker()


def add_clients(df: pd.DataFrame, n_new: int, as_of: date = None) -> pd.DataFrame:
    """
    Append n_new newly-onboarded clients to the clients DataFrame.
    Returns updated DataFrame. Does not touch employees or shifts.
    """
    if as_of is None:
        as_of = date.today()

    if df.empty:
        next_id = 1
    else:
        next_id = int(df["client_id"].max()) + 1

    new_rows = []
    for i in range(n_new):
        weekly_hours = random.choice([4, 6, 8, 10, 14, 20, 28, 40])

        client = {
            "client_id": next_id + i,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.postcode(),
            "primary_phone": fake.phone_number(),
            "payer_type": random.choice(PAYER_TYPES),
            "care_type": random.choice(CARE_TYPES),
            "required_position": random.choice(CLIENT_REQUIRED_POSITIONS),
            "status": "Active",
            "start_of_care_date": as_of,
            "end_of_care_date": None,
            "weekly_authorized_hours": weekly_hours,
            "emergency_contact": fake.name(),
            "emergency_contact_phone": fake.phone_number(),
        }
        new_rows.append(client)

    new_df = pd.DataFrame(new_rows)
    return pd.concat([df, new_df], ignore_index=True)


def discharge_clients(df: pd.DataFrame, max_discharge: int = 2, as_of: date = None) -> pd.DataFrame:
    """
    Randomly discharge up to max_discharge active clients.
    Returns updated DataFrame.
    """
    if as_of is None:
        as_of = date.today()

    active = df[df["status"] == "Active"]
    if active.empty:
        return df

    n_discharge = random.randint(0, min(max_discharge, len(active)))
    if n_discharge == 0:
        return df

    discharge_statuses = [
        "Discharged - Completed",
        "Discharged - Hospitalized",
        "Discharged - Deceased",
        "Discharged - Family Request",
    ]
    weights = [0.55, 0.2, 0.05, 0.2]

    chosen = active.sample(n=n_discharge, random_state=random.randint(0, 9999))
    for idx in chosen.index:
        df.at[idx, "status"] = random.choices(discharge_statuses, weights=weights, k=1)[0]
        df.at[idx, "end_of_care_date"] = as_of

    return df
