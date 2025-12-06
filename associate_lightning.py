import pandas as pd
import xarray as xr
import pandas as pd
import numpy as np

from CGF_Interp_5 import CGF_Interp_5

# Read in historical fire data as a dataframe
fire_data = pd.read_csv('NFDB_point_txt/fire_data_2015enriched.csv', sep=',', header=0, dtype={'YEAR': 'str','MONTH': 'str','DAY': 'str', 12: str, 13: str})
#fire_data = fire_data[fire_data['CAUSE'] == 'N'] # Do we want to filter by natural fires???
fire_data['FLASH_DENSITY'] = None

# Read in cs_flash data
flash_path = "avg_daily_flash_active.nc"
flash_set = xr.open_dataset(flash_path)
print(flash_set)

# Pull example datapt
#month = 7
#lat = 50.3
#lon = -120.7
#flash_density = CGF_Interp_Predict(flash_set, month, lat, lon)
#print("Predicted flash density:", flash_density)

# For each historical fire, return the associated flash data
num_fires = len(fire_data)
for index, fire in fire_data.iterrows():
    flash_density = CGF_Interp_5(flash_set, fire['YEAR'], fire['MONTH'], fire['DAY'], fire['LATITUDE'], fire['LONGITUDE'])

    # Associate the flash data to the data frame item
    if flash_density is not None:
        fire_data.at[index, 'FLASH_DENSITY'] = flash_density

    # Print wildfire index 1000 at a time to update progress
    if index % 1000 == 0:
        print("Wildfires scanned:", index, "/", num_fires)

#Output associated fire data from a dataframe to a csv
fire_data.to_csv('fire_data_2015enriched3.csv', index=False, header=True)
print("Wildfire weather association completed successfully!")