import xarray as xr
import numpy as np
from datetime import datetime
from calculate_grid_cell_area import calculate_grid_cell_area

def CGF_Interp(ds, year, month, day, lat, lon):
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

        # Slice day
        da = ds["cg_flashes"].sel(time=np_dt)

        # Perform bilinear interpolation in lat/lon
        out = da.interp(lat=lat, lon=lon)

        # Convert to Python float
        return float(out.values/calculate_grid_cell_area(lat))
    else:
        return None
    
    import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
from calculate_grid_cell_area import calculate_grid_cell_area