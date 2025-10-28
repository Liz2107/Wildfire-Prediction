import pandas as pd
import os
import re
import time
import numpy as np
from pastWeather import pastWeather
from futureWeather import futureWeather
from collections import defaultdict


# Index data files by date
def index_files_by_date(path):
    date_index = defaultdict(list)

    # Define the date pattern as YYYYMMDD
    date_pattern = re.compile(r"\b(\d{8})\b")

    # Loop through directory files
    with os.scandir(path) as files:
        for file in files:

            # Search for YYYYMMDD date pattern in files
            matching_string = date_pattern.search(file.name)

            # If the date pattern is found, add the file path to the date index
            if matching_string:
                date = matching_string.group(1)
                date_index[date].append(file.path)

    # Returns {date_str: [paths]} format
    return date_index

# Index all the MERRA2 weather data files by date
date_index = index_files_by_date("Data")

# Predict an example future weather value
month = 9
day = 9
latitude = 54.5692
longitude = -126.9287
specific_humidity, temp, precip_ice, precip_water, precip_vapor, wind = futureWeather(month, day, latitude, longitude, date_index)
print("Predicted weather data:", specific_humidity, temp, precip_ice, precip_water, precip_vapor, wind)

# Read in historical fire data as a dataframe
fire_data = pd.read_csv('NFDB_point_txt/NFDB_point_20240613.txt', sep=',', header=0, dtype={'YEAR': 'str','MONTH': 'str','DAY': 'str', 12: str, 13: str})
#fire_data = fire_data[fire_data['CAUSE'] == 'N'] # Do we want to filter by natural fires???
fire_data['SPECIFIC_HUMIDITY'] = None
fire_data['TEMP'] = None
fire_data['PRECIP_ICE'] = None
fire_data['PRECIP_WATER'] = None
fire_data['PRECIP_VAPOR'] = None
fire_data['WIND'] = None

# For each historical fire, return the associated weather data
num_fires = len(fire_data)
for index, fire in fire_data.iterrows():
    specific_humidity, temp, precip_ice, precip_water, precip_vapor, wind = pastWeather(fire['YEAR'], fire['MONTH'], fire['DAY'], fire['LATITUDE'], fire['LONGITUDE'], date_index)

    # Associate the weather data to the data frame item
    if specific_humidity is not None:
        fire_data.at[index, 'SPECIFIC_HUMIDITY'] = specific_humidity
        fire_data.at[index, 'TEMP'] = temp
        fire_data.at[index, 'PRECIP_ICE'] = precip_ice
        fire_data.at[index, 'PRECIP_WATER'] = precip_water
        fire_data.at[index, 'PRECIP_VAPOR'] = precip_vapor
        fire_data.at[index, 'WIND'] = wind

    # Print wildfire index 1000 at a time to update progress
    if index % 1000 == 0:
        print("Wildfires scanned:", index, "/", num_fires)

# Output associated fire data from a dataframe to a csv
fire_data.to_csv('fire_data_processed.csv', index=False, header=True)
print("Wildfire weather association completed successfully!")