from faker import Faker
import random
from datetime import date
from .constants import POSITIONS, RATINGS, EDUCATION, LANGUAGES


fake = Faker()

import pandas as pd

def hire_employees(df, n_new: int):
    if df.empty:
        next_id = 1
    else:
        next_id = df["employee_id"].max() + 1

    new_rows = []

    for i in range(n_new):
        dob = fake.date_of_birth(minimum_age=18, maximum_age=75)
        age = date.today().year - dob.year - (
    (date.today().month, date.today().day) < (dob.month, dob.day)
)

        employee = {
            "employee_id": next_id + i,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "address": fake.street_address(),
            "city": fake.city(),
            "state": fake.state_abbr(),
            "zip": fake.postcode(),
            "primary_phone": fake.phone_number(),
            "email": fake.email(),
            "status": "Active",
            "last_shift_date": None,
            "position": random.choice(POSITIONS),
            "base_pay_rate": round(random.uniform(16, 75), 2),
            "current_rating": random.choice(RATINGS),
            "last_appraisal_date": None,
            "next_appraisal_date": None,
            "hire_date": date.today(),
            "terminated_date": None,
            "rehire_date": None,
            "cpr_date": fake.date_between(start_date="-2y", end_date="+1y"),
            "pto_balance": random.randint(0, 40),
            "commitment_hours": random.randint(0, 40),
            "age": age,
            "dob": dob,
            "gender": random.choice(["Male", "Female"]),
            "education": random.choice(EDUCATION),
            "languages": random.choice(LANGUAGES),
            "emergency_contact": fake.name(),
            "emergency_contact_phone": fake.phone_number(),
            "emergency_instructions": fake.sentence(),
        }

        new_rows.append(employee)

    new_df = pd.DataFrame(new_rows)

    return pd.concat([df, new_df])
