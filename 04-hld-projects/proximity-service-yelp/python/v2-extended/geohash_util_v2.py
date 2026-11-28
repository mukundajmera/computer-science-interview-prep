"""v2 geohash utilities: parity copy of v1 (improvements live in proximity_service_v2)."""

import math
from typing import Tuple, List

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
BASE32_MAP = {c: i for i, c in enumerate(BASE32)}

def encode(lat: float, lon: float, precision: int = 6) -> str:
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    geohash = []
    bits = [16, 8, 4, 2, 1]
    bit = 0
    ch = 0
    even = True

    while len(geohash) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2.0
            if lon >= mid:
                ch |= bits[bit]
                lon_interval[0] = mid
            else:
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2.0
            if lat >= mid:
                ch |= bits[bit]
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid
        
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash.append(BASE32[ch])
            bit = 0
            ch = 0

    return "".join(geohash)

def decode(geohash: str) -> Tuple[float, float]:
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    even = True

    for char in geohash:
        val = BASE32_MAP[char]
        for bit in [16, 8, 4, 2, 1]:
            if even:
                mid = (lon_interval[0] + lon_interval[1]) / 2.0
                if val & bit:
                    lon_interval[0] = mid
                else:
                    lon_interval[1] = mid
            else:
                mid = (lat_interval[0] + lat_interval[1]) / 2.0
                if val & bit:
                    lat_interval[0] = mid
                else:
                    lat_interval[1] = mid
            even = not even
            
    lat = (lat_interval[0] + lat_interval[1]) / 2.0
    lon = (lon_interval[0] + lon_interval[1]) / 2.0
    return lat, lon

def get_dimensions(precision: int) -> Tuple[float, float]:
    lat_dim = 180.0
    lon_dim = 360.0
    for i in range(precision * 5):
        if i % 2 == 0:
            lon_dim /= 2.0
        else:
            lat_dim /= 2.0
    return lat_dim, lon_dim

def get_neighbors(geohash: str) -> List[str]:
    if not geohash:
        return []
    lat, lon = decode(geohash)
    lat_dim, lon_dim = get_dimensions(len(geohash))
    
    neighbors = []
    for dlat in [-lat_dim, 0.0, lat_dim]:
        for dlon in [-lon_dim, 0.0, lon_dim]:
            if dlat == 0.0 and dlon == 0.0:
                continue
            
            nlat = lat + dlat
            nlon = lon + dlon
            
            if nlat > 90.0 or nlat < -90.0:
                continue
            if nlon > 180.0:
                nlon -= 360.0
            elif nlon < -180.0:
                nlon += 360.0
                
            neighbors.append(encode(nlat, nlon, len(geohash)))
            
    return list(set(neighbors))

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2)
    a = max(0.0, min(1.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c
