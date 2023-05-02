import pandas as pd
import numpy as np

# Read metadata from Github
url_meta = "https://github.com/CenterForTheBuiltEnvironment/ashrae-db-II/raw/master/v2.1.0/db_metadata.csv"
df_meta = pd.read_csv(url_meta)

# Read database from Github
url_measurements = "https://github.com/CenterForTheBuiltEnvironment/ashrae-db-II/raw/master/v2.1.0/db_measurements_v2.1.0.csv.gz"
df_measurements = pd.read_csv(url_measurements)

# Fill the missing values in the outdoor temperature column 
df_acm2['t_out_combined'] = df_acm2['t_out_isd'].fillna(df_acm2['t_out'])

# Remove original temperature columns
df_acm2 = df_acm2.drop(columns=['t_out_isd', 't_out'])

# Merge metadata and databased by office buildings
df_acm2 = df_acm2.merge(df_meta[['building_id', 'region', 'building_type', 'cooling_type', 'records']], on='building_id', how='left')
df_acm2 = df_acm2[df_acm2['building_type'] == 'office']
df_acm2 = df_acm2.drop(columns=['building_type'])