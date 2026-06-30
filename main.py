import pandas as pd
from Scripts.simulate_day import simulate_day
import os

# Path to your dataset
DATA_PATH = r"Datasets/Dataset1.csv"

# Load existing employee data if it exists, otherwise start empty
if os.path.exists(DATA_PATH):
    df = pd.read_csv(DATA_PATH)
else:
    df = pd.DataFrame()

# Simulate 1 day
df = simulate_day(df, max_hire=4, max_fire=3)

# Save updated DataFrame back to CSV
df.to_csv(DATA_PATH, index=False)

print("\n--- Final Employee Data ---")
print(df)
