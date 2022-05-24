import pandas as pd

df = pd.read_csv(
    "./data/db_measurements_v21.csv.gzip", low_memory=False, compression="gzip"
)
