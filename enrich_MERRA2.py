import pandas as pd
import os
import re
from pastWeather import pastWeather
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

# Read in data
fileNames = ['fire_data_2016enriched','fire_data_2017enriched','fire_data_2018enriched','fire_data_2019enriched','fire_data_2020enriched','fire_data_2021enriched','fire_data_2022enriched','fire_data_2023enriched']
for fileName in fileNames:

    fire_data = pd.read_csv(fileName + '.csv', sep=',', header=0)

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
    fire_data.to_csv(fileName + '2.csv', index=False, header=True)
    print("Wildfire weather association completed successfully!")