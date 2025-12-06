import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import silhouette_score

import statsmodels.api as sm

# Find optimal k for k means clustering using silhouette score
def optimal_cluster_count(data, k_min=2, k_max=20):
    best_k = k_min
    best_score = -1

    for k in range(k_min, k_max + 1):
        print(f"Attempting clustering with {k} clusters...")
        model = KMeans(n_clusters=k, random_state=42).fit(data)
        labels = model.labels_

        # avoid silhouette calc failure if cluster collapse occurs
        if len(set(labels)) <= 1:
            continue

        score = silhouette_score(data, labels)

        if score > best_score:
            best_k, best_score = k, score

    return best_k

# Read in enriched data, remove unknown fires
fire_data = pd.read_csv("fire_data_enriched3_date.csv")
fire_data = fire_data.dropna(subset=["FLASH_DENSITY","LATITUDE", "LONGITUDE"])
fire_data = fire_data[fire_data["CAUSE"] != "U"]

# target var, F_O = 1 if N, otherwise F_O = 0
fire_data["FIRE_OCCURRENCE"] = (fire_data['CAUSE'] == 'N').astype(int)

# Set up location dataframe
coords = fire_data[["LATITUDE", "LONGITUDE"]]

# Days since start of dataset, used for clustering
fire_data['DATE'] = pd.to_datetime(fire_data['DATE'])
fire_data["TIME_INDEX"] = (fire_data["DATE"] - fire_data["DATE"].min()).dt.days

scaler = MinMaxScaler()
fire_data["TIME_SCALED"] = scaler.fit_transform(fire_data[["TIME_INDEX"]])

# Review
print(fire_data)
print(coords)
print("NaNs per column:\n", fire_data.isna().sum())

# Clustering ------------------------------------------------------------------

# KMeans spatial clustering with optimal spatial k
best_k = 2 #optimal_cluster_count(coords,2,20)
print(f"Using optimal number of spatial clusters: {best_k}")
kmeans = KMeans(n_clusters=best_k, random_state=42)
fire_data["SPATIAL_CLUSTER"] = kmeans.fit_predict(coords)

print("Missing clusters:", fire_data["SPATIAL_CLUSTER"].isna().sum())
print(fire_data["SPATIAL_CLUSTER"].value_counts(dropna=False))

# KMeans temporal clustering within each spatial cluster
temporal_cluster_labels = []

for cluster_id in sorted(fire_data["SPATIAL_CLUSTER"].unique()):

    subset = fire_data[fire_data["SPATIAL_CLUSTER"] == cluster_id]
    time_vals = subset[["TIME_SCALED"]].values

    if len(subset) < 10:
        # too small to cluster further
        temporal_cluster_labels.extend([0] * len(subset))
        continue

    # Determine optimal temporal k
    best_k_time = optimal_cluster_count(time_vals, k_min=2, k_max=20)
    print(f"Using optimal number of spatial clusters: {best_k_time}")

    kmeans_time = KMeans(n_clusters=best_k_time, random_state=42)
    labels = kmeans_time.fit_predict(time_vals)

    temporal_cluster_labels.extend(labels)

fire_data["TEMPORAL_CLUSTER"] = temporal_cluster_labels

# Spatiotemporal clustering
fire_data["SPATIOTEMPORAL_CLUSTER"] = (
    fire_data["SPATIAL_CLUSTER"].astype(str) + "_" + fire_data["TEMPORAL_CLUSTER"].astype(str)
)

fire_data["SPATIOTEMPORAL_CLUSTER"] = (
    fire_data["SPATIOTEMPORAL_CLUSTER"].astype("category").cat.codes
)

# Logistic regression ---------------------------------------------------------

# Select logistic regression params
features = ["FLASH_DENSITY", "SPATIOTEMPORAL_CLUSTER"]
target = "FIRE_OCCURRENCE"

X = fire_data[features]
y = fire_data[target]

# Identify numeric and categorical features
numeric_features = ["FLASH_DENSITY"]
categorical_features = ["SPATIOTEMPORAL_CLUSTER"]

# Preprocessing
print("Attempting preprocessing...")
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(drop="first"), categorical_features)
    ]
)

# Fit and transform data, add intercept
X_processed = preprocessor.fit_transform(X)
feature_names = preprocessor.get_feature_names_out()

if hasattr(X_processed, "toarray"):
    X_processed = X_processed.toarray()
X_processed = sm.add_constant(X_processed)

X_df = pd.DataFrame(X_processed)
X_df = X_df.replace([np.inf, -np.inf], np.nan)  
valid_rows = X_df.notna().all(axis=1) & y.notna()

X_processed = X_df[valid_rows]
y = y[valid_rows]

# Run logistic regression
print("Running logistic regression...")
logit_model = sm.Logit(y, X_processed).fit()

# Print model statistics
print("\nLogistic regression results\n")
print(logit_model.summary())

# Get odds ratios
params = logit_model.params
conf = logit_model.conf_int()
conf['OR'] = params
conf.columns = ['2.5%', '97.5%', 'Odds Ratio']
conf = np.exp(conf)

print("\nOdds ratios\n")
print(conf)

print(feature_names)