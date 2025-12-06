import xarray as xr
import numpy as np

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize, ListedColormap
import contextily as ctx

from calculate_grid_cell_area import calculate_grid_cell_area

ds = xr.open_dataset("avg_daily_flash_active.nc", chunks={"time": 50, "lat": 200, "lon": 200})

# Identify slice of interest
subset = ds.sel(
    lat=slice(65, 45),
    lon=slice(-140, -100),
    time=slice("2023-08-01", "2023-08-31")
)

start_date = pd.to_datetime(subset.time.values[0]).strftime("%Y-%m-%d")
end_date   = pd.to_datetime(subset.time.values[-1]).strftime("%Y-%m-%d")

print(subset)

# Apply density calculations to sliced dataset using dask
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

raster = mean_density.rio.write_crs("EPSG:4326")
raster_3857 = raster.rio.reproject("EPSG:3857")

# Normalize values
norm = Normalize(vmin=float(raster_3857.min()), vmax=float(raster_3857.max()))

# Build alpha-gradient colormap
cmap = plt.cm.plasma
colors = cmap(np.linspace(0, 1, 256))
alpha = np.linspace(0.1, 1, 256)  # fade from transparent
colors[:, -1] = alpha
transparent_cmap = ListedColormap(colors)

#  Plotting
fig, ax = plt.subplots(figsize=(12, 10))

im = raster_3857.plot(
    ax=ax,
    cmap=transparent_cmap,
    norm=norm,
    add_colorbar=False
)

ctx.add_basemap(ax, crs="EPSG:3857", source=ctx.providers.CartoDB.Positron)

ax.set_title(f"Mean Lightning Flash Density\n{start_date} → {end_date}")
cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Flash Density [Flashes/km$^2$]")
ax.set_axis_off()

plt.show()