"""
v2-extended proximity service.

Improvements over v1-basic (each has dedicated tests):

1. Dense-area pagination with exact distances on the candidate set
   (FOLLOW-UPS.md #3): search results are strictly paginated (page_size +
   page) and the response carries the total match count, so a Manhattan
   cell with thousands of businesses never floods the client. Exact
   haversine distances are still computed for every candidate before
   ranking, so page 1 is always the true closest set.

2. Secondary attribute filtering (FOLLOW-UPS.md #4): businesses carry
   category, rating and open_now attributes, and search accepts filters
   on them, applied before distance ranking - the in-memory answer to
   "open now, highly rated, within 2km" that pure geohash lookup cannot
   express.

3. Geohash-prefix sharding with observability (FOLLOW-UPS.md #1 10x
   scale): the index is partitioned into shards keyed by the first
   geohash character, the way a Redis cluster would hash by geohash, and
   a query scans only the shards its 9 cells live in. The shard count
   each query touches is exposed as a metric.
"""

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import geohash_util_v2


@dataclass
class Business:
    id: str
    lat: float
    lon: float
    category: str = ""
    rating: float = 0.0
    open_now: bool = True


class ProximityService:
    def __init__(self):
        self.businesses: Dict[str, Business] = {}
        # Improvement #3: shard key -> {geohash: business ids}
        self.shards: Dict[str, Dict[str, Set[str]]] = {}
        self.lock = threading.RLock()
        # Metrics (improvements #1 and #3).
        self.queries_run = 0
        self.last_query_shards_touched = 0

    @staticmethod
    def _validate_coordinates(lat: float, lon: float):
        if not -90.0 <= lat <= 90.0:
            raise ValueError("latitude out of range: %r" % (lat,))
        if not -180.0 <= lon <= 180.0:
            raise ValueError("longitude out of range: %r" % (lon,))

    @staticmethod
    def _shard_key(geohash: str) -> str:
        return geohash[0]

    def add_business(self, business: Business):
        self._validate_coordinates(business.lat, business.lon)
        with self.lock:
            # Remove if exists
            self.remove_business(business.id)

            self.businesses[business.id] = business
            geohash = geohash_util_v2.encode(business.lat, business.lon, precision=6)
            shard = self.shards.setdefault(self._shard_key(geohash), {})
            if geohash not in shard:
                shard[geohash] = set()
            shard[geohash].add(business.id)

    def remove_business(self, business_id: str):
        with self.lock:
            if business_id in self.businesses:
                business = self.businesses[business_id]
                geohash = geohash_util_v2.encode(business.lat, business.lon, precision=6)
                shard_key = self._shard_key(geohash)
                shard = self.shards.get(shard_key, {})
                if geohash in shard:
                    shard[geohash].discard(business_id)
                    if not shard[geohash]:
                        del shard[geohash]
                if shard_key in self.shards and not self.shards[shard_key]:
                    del self.shards[shard_key]
                del self.businesses[business_id]

    def _search(self, lat: float, lon: float, radius_km: float,
                category: Optional[str] = None,
                min_rating: Optional[float] = None,
                open_now: Optional[bool] = None) -> List[Business]:
        """Candidates from the 9 cells of the touched shards, filtered,
        exact-distance ranked."""
        self._validate_coordinates(lat, lon)
        precision = self._get_precision_for_radius(radius_km)
        center_geohash = geohash_util_v2.encode(lat, lon, precision)
        geohashes_to_search = [center_geohash] + geohash_util_v2.get_neighbors(center_geohash)

        results = []
        with self.lock:
            touched_shards = set()
            for geohash in geohashes_to_search:
                shard_key = self._shard_key(geohash)
                shard = self.shards.get(shard_key)
                if not shard:
                    continue
                touched_shards.add(shard_key)
                for indexed_geohash, business_ids in shard.items():
                    if indexed_geohash.startswith(geohash):
                        for b_id in business_ids:
                            b = self.businesses[b_id]
                            # Improvement #2: attribute filters first.
                            if category is not None and b.category != category:
                                continue
                            if min_rating is not None and b.rating < min_rating:
                                continue
                            if open_now is not None and b.open_now != open_now:
                                continue
                            dist = geohash_util_v2.haversine_distance(lat, lon, b.lat, b.lon)
                            if dist <= radius_km:
                                results.append((dist, b))
            self.queries_run += 1
            self.last_query_shards_touched = len(touched_shards)

        results.sort(key=lambda x: x[0])
        return [b for dist, b in results]

    def get_nearby_businesses(self, lat: float, lon: float, radius_km: float) -> List[Business]:
        """v1-compatible: every match within the radius, distance-ranked."""
        return self._search(lat, lon, radius_km)

    def search_nearby(self, lat: float, lon: float, radius_km: float,
                      category: Optional[str] = None,
                      min_rating: Optional[float] = None,
                      open_now: Optional[bool] = None,
                      page_size: Optional[int] = None,
                      page: int = 1) -> Dict[str, object]:
        """Improvements #1 and #2: filtered, paginated search.

        Returns {"businesses": [...], "total": N, "page": page,
        "page_size": page_size}. With no filters and no page_size this is
        exactly v1's full result list. Pagination is strict: page 1 is
        the closest page_size businesses after exact-distance ranking.
        """
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size is not None and page_size <= 0:
            raise ValueError("page_size must be positive")

        matches = self._search(lat, lon, radius_km, category, min_rating, open_now)
        total = len(matches)

        if page_size is not None:
            start = (page - 1) * page_size
            matches = matches[start:start + page_size]

        return {
            "businesses": matches,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def _get_precision_for_radius(self, radius_km: float) -> int:
        if radius_km <= 0.15: return 7
        if radius_km <= 1.2: return 6
        if radius_km <= 5.0: return 5
        if radius_km <= 40.0: return 4
        if radius_km <= 150.0: return 3
        if radius_km <= 1200.0: return 2
        return 1
