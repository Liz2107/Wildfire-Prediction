import pandas as pd

# Load dataset
years = range(2017, 2024)
dfs = [pd.read_csv(f'NFDB_enriched_population/fire_data_{y}enriched4.csv') for y in years]
df = pd.concat(dfs)
# Filter out unknown cause values
df_filtered = df[(df["YEAR"].between(2017, 2023)) & (df["CAUSE"].isin(["N", "H"]))]

# Calculate percentage breakdown
percentages = df_filtered["CAUSE"].value_counts(normalize=True) * 100

print("Fire Cause Percentages (excluding unknowns):")
print(percentages.round(2).astype(str) + "%")

# Optional: print raw counts
print("\nCounts:")
print(df_filtered["CAUSE"].value_counts())