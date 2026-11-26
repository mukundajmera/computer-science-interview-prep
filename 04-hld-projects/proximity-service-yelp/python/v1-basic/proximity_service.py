from dataclasses import dataclass
from typing import Dict, List, Set
import geohash_util
import threading

@dataclass
class Business:
    id: str
    lat: float
    lon: float

class ProximityService:
    def __init__(self):
        self.businesses: Dict[str, Business] = {}
        self.geohash_index: Dict[str, Set[str]] = {}
        self.lock = threading.RLock()
        
    def add_business(self, business: Business):
        with self.lock:
            # Remove if exists
            self.remove_business(business.id)
            
            self.businesses[business.id] = business
            geohash = geohash_util.encode(business.lat, business.lon, precision=6)
            if geohash not in self.geohash_index:
                self.geohash_index[geohash] = set()
            self.geohash_index[geohash].add(business.id)
            
    def remove_business(self, business_id: str):
        with self.lock:
            if business_id in self.businesses:
                business = self.businesses[business_id]
                geohash = geohash_util.encode(business.lat, business.lon, precision=6)
                if geohash in self.geohash_index:
                    self.geohash_index[geohash].discard(business_id)
                    if not self.geohash_index[geohash]:
                        del self.geohash_index[geohash]
                del self.businesses[business_id]

    def get_nearby_businesses(self, lat: float, lon: float, radius_km: float) -> List[Business]:
        precision = self._get_precision_for_radius(radius_km)
        center_geohash = geohash_util.encode(lat, lon, precision)
        
        geohashes_to_search = [center_geohash] + geohash_util.get_neighbors(center_geohash)
        
        results = []
        with self.lock:
            for geohash in geohashes_to_search:
                # We need to find all indexed geohashes that start with our search prefix
                for indexed_geohash, business_ids in self.geohash_index.items():
                    if indexed_geohash.startswith(geohash):
                        for b_id in business_ids:
                            b = self.businesses[b_id]
                            dist = geohash_util.haversine_distance(lat, lon, b.lat, b.lon)
                            if dist <= radius_km:
                                results.append((dist, b))
                                
        # Sort by distance
        results.sort(key=lambda x: x[0])
        return [b for dist, b in results]

    def _get_precision_for_radius(self, radius_km: float) -> int:
        if radius_km <= 0.15: return 7
        if radius_km <= 1.2: return 6
        if radius_km <= 5.0: return 5
        if radius_km <= 40.0: return 4
        if radius_km <= 150.0: return 3
        if radius_km <= 1200.0: return 2
        return 1
