import numpy as np
import xarray as xr

# Predicts the future weather data associated with a specific date and location
def futureWeather(month, day, latitude, longitude, date_index):
    # Check that data is valid
    if (month is not None and day is not None and latitude is not None and longitude is not None) and (latitude > 25 and latitude < 84) and (longitude > -172 and longitude < -52):
        specific_humidity = []
        temp = []
        precip_ice = []
        precip_water = []
        precip_vapor = []
        wind = []

        # Make sure wildfire date is in YYYYMMDD format
        month = str(month)
        day = str(day)

        if len(month) == 1:
            month = '0'+month
        if len(day) == 1:
            day = '0'+day

        # Make a list of years to check weather data for
        years = list(range(1980, 2025))

        # Make a list of dates to check weather data for
        dates = []
        for year in years:
            dates.append(str(year)+month+day)

        # Check the weather for each date
        for date in dates:
            # Find each data file to read in from the indexed MERRA2 data files
            fileNames = date_index.get(date, [])
            if fileNames:
                # Open the weather data file for the given date
                data = xr.open_dataset(fileNames[0], cache=False)
                    # Variables are QV2M, T2M, TQI, TQL, TQV, U2M, V2M

                # Read in data values for a wildfire using bilinear interpolation
                data = data.interp(lat=latitude,lon=longitude)

                #QV2M:
                #    standard_name:   2-meter_specific_humidity
                #    long_name:       2-meter_specific_humidity
                #    units:           kg kg-1
                #    cell_methods:    time: mean
                #    fmissing_value:  1e+15
                #    vmax:            1e+15
                #    vmin:            -1e+15
                specific_humidity.append(data['QV2M'].values[0])

                # T2M:
                #     standard_name:   2-meter_air_temperature
                #     long_name:       2-meter_air_temperature
                #     units:           K
                #     cell_methods:    time: mean
                #     fmissing_value:  1e+15
                #     vmax:            1e+15
                #     vmin:            -1e+15
                temp.append(data['T2M'].values[0])

                # TQI:
                #     standard_name:   total_precipitable_ice_water
                #     long_name:       total_precipitable_ice_water
                #     units:           kg m-2
                #     cell_methods:    time: mean
                #     fmissing_value:  1e+15
                #     vmax:            1e+15
                #     vmin:            -1e+15
                precip_ice.append(data['TQI'].values[0])

                # TQL:
                #     standard_name:   total_precipitable_liquid_water
                #     long_name:       total_precipitable_liquid_water
                #     units:           kg m-2
                #     cell_methods:    time: mean
                #     fmissing_value:  1e+15
                #     vmax:            1e+15
                #     vmin:            -1e+15
                precip_water.append(data['TQL'].values[0])

                # TQV:
                #     standard_name:   total_precipitable_water_vapor
                #     long_name:       total_precipitable_water_vapor
                #     units:           kg m-2
                #     cell_methods:    time: mean
                #     fmissing_value:  1e+15
                #     vmax:            1e+15
                #     vmin:            -1e+15
                precip_vapor.append(data['TQV'].values[0])

                # U2M:
                #     standard_name:   2-meter_eastward_wind
                #     long_name:       2-meter_eastward_wind
                #     units:           m s-1
                #     cell_methods:    time: mean
                #     fmissing_value:  1e+15
                #     vmax:            1e+15
                #     vmin:            -1e+15
                east_wind = data['U2M'].values[0]

                # V2M:
                #     standard_name:   2-meter_northward_wind
                #     long_name:       2-meter_northward_wind
                #     units:           m s-1
                #     cell_methods:    time: mean
                #     fmissing_value:  1e+15
                #     vmax:            1e+15
                #     vmin:            -1e+15
                north_wind = data['V2M'].values[0]

                # Calculate wind magnitude
                wind.append(np.sqrt(east_wind**2 + north_wind**2))

        # Return the average weather values over all years of data
        return sum(specific_humidity)/len(specific_humidity), sum(temp)/len(temp), sum(precip_ice)/len(precip_ice), sum(precip_water)/len(precip_water), sum(precip_vapor)/len(precip_vapor), sum(wind)/len(wind)
    else:
        return None, None, None, None, None, None