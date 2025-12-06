import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
import numpy as np
import pandas as pd

# Population density association function
def sample_population_density(df):
    pop_values = np.full(len(df), np.nan)
    raster_cache = {}

    # Split dataset into annual subsets and associate each
    for year in df["YEAR"].unique():
        subset_idx = df.index[df["YEAR"] == year]
        sub = df.loc[subset_idx]

        # Obtain population density for the chosen year
        tif_path = f"pop_densities/can_pop_{year}_CN_1km_R2025A_UA_v1.tif"
        # Caching for efficiency
        if year not in raster_cache:
            ds = rasterio.open(tif_path)
            raster_cache[year] = ds

        ds = raster_cache[year]

        # Bilinear interpolation between raster gridpts
        with WarpedVRT(ds, resampling=Resampling.bilinear) as vrt:
            coords = list(zip(sub["LONGITUDE"], sub["LATITUDE"]))
            vals = [v[0] for v in vrt.sample(coords)]

        pop_values[subset_idx] = np.maximum(vals, 0)  # clamp negatives

    df["POP_DENSITY"] = pop_values
    return df


# Read in fire data
data = pd.read_csv('NFDB_enriched_lightning/*.csv', sep=',', header=0)
data = sample_population_density(data)

# Filter out missing values
data = data[data["POP_DENSITY"].notna()]

# Output
data.to_csv('NFDB_enriched_population/fire_pop_data.csv', index=False, header=True)