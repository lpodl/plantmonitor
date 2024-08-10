"""
Concatenate all DataFrames from one day into a single DataFrame
"""

import os
import pandas as pd
import sys

DATA_DIR = "./sensor_data"

if len(sys.argv) < 2:
    print("Please provide a date as an argument.")
    print("e.g. python aggregate_data.py '2024-08-07'")
    sys.exit(1)
date = sys.argv[1]
csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv") and date in f]
dataframes = []

for file in csv_files:
    path = os.path.join(DATA_DIR, file)
    df = pd.read_csv(path)
    dataframes.append(df)

aggregated_df = pd.concat(dataframes, ignore_index=True)
aggregated_df.to_csv(f"./sensor_data/{date}.csv", index=False)
