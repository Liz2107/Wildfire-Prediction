import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
from calculate_grid_cell_area import calculate_grid_cell_area

def CGF_Interp_5(ds, year, month, day, lat, lon):
    if ((year is not None and month is not None and day is not None and lat is not None and lon is not None) and 
        (lat > 40.05 and lat < 74.95) and 
        (lon > -144.9 and lon < -50.05)):
        
        if isinstance(month, str):
            if len(month) == 1:
                month = '0'+month
            if len(day) == 1:
                day = '0'+day
            date = year+month+day
        elif isinstance(month, int):
            if month < 10:
                month = '0'+str(month)
            if day < 10:
                day = '0'+str(day)
        date = str(day)+str(month)+str(year)

        try:
            m_int = int(month)
            d_int = int(day)
        except ValueError:
            return None
        if m_int == 0 or d_int == 0:
            return None
        
        dt = datetime.strptime(date, "%d%m%Y")
        np_dt = np.datetime64(dt.date(), 'D')
        pd_dt = pd.Timestamp(np_dt)

        start_dt = pd_dt - pd.Timedelta(days=5)  # 2 days before
        end_dt = pd_dt   

        # Slice day
        #da = ds["cg_flashes"].sel(time=np_dt)
        da_time = ds["cg_flashes"].sel(time=slice(start_dt, end_dt))

        # Perform bilinear interpolation in lat/lon
        da_space = da_time.interp(lat=lat, lon=lon)

        out = da_space.mean(dim="time")

        # Convert to Python float
        return float(out.values/calculate_grid_cell_area(lat))
    else:
        return None