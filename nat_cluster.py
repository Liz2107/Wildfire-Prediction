import pandas as pd
import numpy as np
from datetime import datetime

from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import silhouette_score

import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import matplotlib.colors as mcolors

# Cluster count optimization using silhouette score
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

# Read in enriched data, filter to natural fires
fire_data = pd.read_csv("fire_data_2023enriched3_date.csv")
fire_data = fire_data.dropna(subset=["FLASH_DENSITY","LATITUDE", "LONGITUDE"])
fire_data = fire_data[fire_data["CAUSE"] == "N"]

# Set up location dataframe
coords = fire_data[["LATITUDE", "LONGITUDE"]]

# Days since start of dataset, used for clustering
fire_data['DATE'] = pd.to_datetime(fire_data['DATE'])
fire_data['doy'] = fire_data['DATE'].dt.dayofyear
fire_data["TIME_INDEX"] = (fire_data["DATE"] - fire_data["DATE"].min()).dt.days
# Scale time data so that the number of days is not unfairly weighted in the model
scaler = MinMaxScaler()
fire_data["TIME_SCALED"] = scaler.fit_transform(fire_data[["TIME_INDEX"]])

# Clustering
# KMeans spatial clustering with optimal spatial k
best_k = 2 #optimal_cluster_count(coords,2,20)
print(f"Using optimal number of spatial clusters: {best_k}")
kmeans = KMeans(n_clusters=best_k, random_state=42)
fire_data["SPATIAL_CLUSTER"] = kmeans.fit_predict(coords)

print(fire_data["SPATIAL_CLUSTER"].value_counts(dropna=False))

# KMeans temporal clustering within each spatial cluster
temporal_cluster_labels = []
# Cluster within each spatial cluster to identify distinct spatial trends
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

print(fire_data["SPATIOTEMPORAL_CLUSTER"].value_counts(dropna=False))

# Plotting
gdf = gpd.GeoDataFrame(
    fire_data,
    geometry=gpd.points_from_xy(fire_data.LONGITUDE, fire_data.LATITUDE),
    crs="EPSG:4326"
)
gdf = gdf.to_crs(epsg=3857)

# Generate a plot of each cluster
unique_clusters = sorted(gdf['SPATIOTEMPORAL_CLUSTER'].unique())
for cluster in unique_clusters:
    subset = gdf[gdf['SPATIOTEMPORAL_CLUSTER'] == cluster].sort_values('DATE')
    
    # Normalize date range for colormap
    vmin, vmax = 1, 365
    norm = mcolors.Normalize(vmin, vmax)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot wildfire points colored by date progression
    scatter = ax.scatter(
        subset.geometry.x,
        subset.geometry.y,
        c=subset['doy'],
        cmap="plasma",
        s=35,
        alpha=0.9,
        norm=norm
    )

    # Basemap for location context
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

    # Styling
    ax.set_title(f"2023 Wildfire Spatio-Temporal Cluster: {cluster}", fontsize=14)
    ax.set_axis_off()

    # Add time colorbar
    month_starts = pd.date_range("2023-01-01", "2023-12-31", freq="MS")  # year doesn't matter
    tick_positions = [d.timetuple().tm_yday for d in month_starts]
    tick_labels = [d.strftime("%b") for d in month_starts]  # Jan, Feb, Mar...

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_ticks(tick_positions)
    cbar.set_ticklabels(tick_labels)
    cbar.set_label("Seasonal Ignition Timing")

    plt.show()