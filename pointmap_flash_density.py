import xarray as xr
import numpy as np

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import contextily as ctx

import rioxarray as rxr

from calculate_grid_cell_area import calculate_grid_cell_area

ds = xr.open_dataset("avg_daily_flash_active.nc", chunks={"time": 50, "lat": 200, "lon": 200})

subset = ds.sel(
    lat=slice(65, 45),
    lon=slice(-140, -100),
    time=slice("2023-07-01", "2023-08-31")
)

print(subset)

cell_area = xr.apply_ufunc(
    calculate_grid_cell_area,
    subset["lat"],
    vectorize=True,
    dask="parallelized",
    output_dtypes=[float]
)

area_aligned = cell_area.broadcast_like(subset["cg_flashes"])
density = subset["cg_flashes"] / area_aligned
mean_density = density.mean(dim="time").compute()

df = mean_density.to_dataframe(name="flash_density").reset_index()
df = df.dropna()

geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

gdf_3857 = gdf.to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(10, 10))

values = gdf_3857["flash_density"]
norm = (values - values.min()) / (values.max() - values.min())
gdf_3857["alpha"] = 0.05 + 0.95 * norm  # range ~0.05 to 1.0

gdf_3857.plot(
    ax=ax,
    column="flash_density",
    cmap="plasma",
    markersize=5,
    legend=True,
    alpha=gdf_3857["alpha"]
)

ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
start_date = pd.to_datetime(subset.time.values[0]).strftime("%Y-%m-%d")
end_date = pd.to_datetime(subset.time.values[-1]).strftime("%Y-%m-%d")

ax.set_title(f"Mean Lightning Flash Density [flashes/km$^2$]\n{start_date} to {end_date}")
ax.set_axis_off()

plt.show()