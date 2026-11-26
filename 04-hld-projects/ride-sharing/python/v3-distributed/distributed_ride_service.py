from dataclasses import dataclass
from typing import List, Protocol, Dict, Tuple, Optional, Set
import threading


@dataclass(frozen=True)
class RideEvent:
    ride_id: str
    event_type: str
    timestamp_millis: int


@dataclass(frozen=True)
class GeoDriverCandidate:
    driver_id: str
    eta_minutes: float
    distance_km: float


@dataclass(frozen=True)
class LocationPoint:
    lat: float
    lng: float
    timestamp_millis: int


class DistributedRideService(Protocol):
    """Distributed ride orchestration contract."""

    def resolve_city_shard(self, pickup_lat: float, pickup_lng: float) -> str: ...
    def replicate_ride_event(self, shard: str, event: RideEvent) -> None: ...
    def reconcile_assignments(self, shard: str) -> None: ...


class GeoSearchIndex(Protocol):
    """Geospatial lookup abstraction for dispatch."""

    def nearby_entities(
        self, lat: float, lng: float, radius_km: float, limit: int
    ) -> List[GeoDriverCandidate]: ...

    def upsert_position(
        self, driver_id: str, lat: float, lng: float, timestamp_millis: int
    ) -> None: ...


class OfflineActivityBuffer(Protocol):
    """Offline route-point buffer for intermittent connectivity."""

    def append_point(self, activity_id: str, point: LocationPoint) -> None: ...
    def flush_batch(self, activity_id: str, max_points: int) -> List[LocationPoint]: ...


@dataclass(frozen=True)
class MatchRequest:
    ride_id: str
    lat: float
    lng: float


class BatchedBipartiteDispatcher:
    def __init__(self, geo_index: GeoSearchIndex):
        self.geo_index = geo_index
        self.pending_requests: List[MatchRequest] = []
        self.lock = threading.RLock()

    def submit_request(self, ride_id: str, lat: float, lng: float) -> None:
        with self.lock:
            self.pending_requests.append(MatchRequest(ride_id, lat, lng))

    def dispatch_batch(self) -> Dict[str, str]:
        """
        Solves minimum-cost bipartite matching to minimize global system pickup ETA.
        Returns a mapping of ride_id -> driver_id.
        """
        with self.lock:
            if not self.pending_requests:
                return {}
            
            requests_to_process = list(self.pending_requests)
            self.pending_requests.clear()

        # Build cost matrix: edges from ride_id to driver_id with eta_minutes as cost
        edges: List[Tuple[str, str, float]] = []
        available_drivers: Set[str] = set()
        
        for req in requests_to_process:
            candidates = self.geo_index.nearby_entities(req.lat, req.lng, radius_km=5.0, limit=10)
            for cand in candidates:
                edges.append((req.ride_id, cand.driver_id, cand.eta_minutes))
                available_drivers.add(cand.driver_id)
                
        # Simple Greedy Approximation for Minimum-Cost Bipartite Matching
        # Sort all possible (ride, driver) edges by ETA
        edges.sort(key=lambda x: x[2])
        
        assigned_rides: Set[str] = set()
        assigned_drivers: Set[str] = set()
        matches: Dict[str, str] = {}
        
        for ride_id, driver_id, eta in edges:
            if ride_id not in assigned_rides and driver_id not in assigned_drivers:
                assigned_rides.add(ride_id)
                assigned_drivers.add(driver_id)
                matches[ride_id] = driver_id
                
        return matches
