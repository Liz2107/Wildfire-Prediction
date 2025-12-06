import pandas as pd
import os

path = "NFDB_enriched_lightning"

dfs = []

for filename in os.listdir(path):
    if filename.endswith(".csv"):
        filepath = os.path.join(path, filename)
        df = pd.read_csv(filepath)
        dfs.append(df)

comb = pd.concat(dfs, ignore_index=True)
comb.to_csv("fire_data_enriched3.csv", index=False)