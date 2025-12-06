import pandas as pd
import matplotlib.pyplot as plt
import calendar

df = pd.read_csv("NFDB_enriched_lightning/fire_data_2023enriched3.csv")
print(df)

# Convert to numeric
df["YEAR"] = pd.to_numeric(df["YEAR"], errors="coerce")
df["MONTH"] = pd.to_numeric(df["MONTH"], errors="coerce")
df["DAY"] = pd.to_numeric(df["DAY"], errors="coerce")

# Create datetime safely
df["DATE"] = pd.to_datetime(
    df[["YEAR", "MONTH", "DAY"]], 
    errors="coerce"
)

# Remove false dates
invalid_dates = df["DATE"].isna().sum()
print(f"Invalid or missing date entries removed: {invalid_dates}")

df = df.dropna(subset=["DATE"]).reset_index(drop=True)

print(df)

# Save changes
#df.to_csv("fire_data_2023enriched3_date.csv", index=False)

# Generate histogram of natural fires
df = df[df["CAUSE"] == "N"]
df["MONTH"] = df["DATE"].dt.month

bins = range(1, 14)

n, bins, patches = plt.hist(df["MONTH"], bins=bins, edgecolor="black")

centers = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins)-1)]
month_labels = [calendar.month_abbr[m] for m in range(1, 13)]

plt.xticks(centers, month_labels)

plt.title("2023 Fire Occurrences by Month")
plt.xlabel("Month")
plt.ylabel("Fire Occurences")

plt.tight_layout()
plt.show()