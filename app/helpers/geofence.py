import math

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in meters between two points 
    on the earth (specified in decimal degrees) using Haversine formula.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999999.0

    # Radius of earth in kilometers
    R = 6371000.0 # Meters

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    r_lat1 = math.radians(lat1)
    r_lat2 = math.radians(lat2)

    a = math.sin(dLat / 2) ** 2 + math.cos(r_lat1) * math.cos(r_lat2) * math.sin(dLon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def is_within_radius(lat1, lon1, lat2, lon2, max_radius_meters):
    dist = calculate_haversine_distance(lat1, lon1, lat2, lon2)
    return dist <= max_radius_meters, dist
