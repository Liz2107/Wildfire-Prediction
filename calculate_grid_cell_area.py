import math

def calculate_grid_cell_area(latitude):
    # Earth's mean radius in kilometers
    R = 6371 

    # Convert latitude to radians
    lat_rad = math.radians(latitude)

    # Length of 0.1 degree of latitude (approximately constant)
    # 1 degree of latitude is approximately 111.19 km
    delta_lat_km = 0.1 * 111.19

    # Length of 0.1 degree of longitude at the given latitude
    # This varies with latitude and is calculated as:
    # (2 * pi * R * cos(latitude)) / 360 * 0.1
    delta_lon_km = (2 * math.pi * R * math.cos(lat_rad)) / 360 * 0.1

    # Approximate area of the cell
    area_sq_km = delta_lat_km * delta_lon_km

    return area_sq_km
