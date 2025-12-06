
import pandas as pd
import xarray as xr

# Test file for messing around with xarray aggregation and visualization

#ds = xr.open_mfdataset("cg_flash_active/*.nc")
#dsa = xr.open_dataset("avg_monthly_flash.nc")
ds = xr.open_dataset("avg_daily_flash_active.nc")

print(ds)
#daily_flash = ds["cg_flashes"].resample(time="D").sum()
#print(daily_flash)
#daily_flash.to_netcdf('avg_daily_flash_active.nc')

#dsr = ds.groupby("time.month").mean(dim="time")
#dsr = ds.resample(time="D").mean()

#print(dsr)

# example query val = dsr['cg_flashes'].sel(month=7, lat=45.0, lon=-90.0, method='nearest').compute().values
    