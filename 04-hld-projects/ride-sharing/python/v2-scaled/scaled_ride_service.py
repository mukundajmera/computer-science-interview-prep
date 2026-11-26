from typing import Protocol, List, Dict, Set
import math
from dataclasses import dataclass


class AssignmentGuard(Protocol):
    def try_assign_driver(self, ride_id: str, driver_id: str, idempotency_key: str) -> bool: ...


class DriverAvailabilityStore(Protocol):
    def mark_available(self, driver_id: str) -> None: ...
    def mark_unavailable(self, driver_id: str) -> None: ...
    def is_available(self, driver_id: str) -> bool: ...


class LocationIngestionService(Protocol):
    def ingest_location(self, driver_id: str, lat: float, lng: float, timestamp_millis: int) -> None: ...


@dataclass(frozen=True)
class HexCell:
    q: int
    r: int
    
    def __str__(self) -> str:
        return f"{self.q},{self.r}"


class H3SpatialIndexer:
    def __init__(self, resolution_step: float = 0.01):
        self.resolution_step = resolution_step
        self.cell_to_drivers: Dict[str, Set[str]] = {}
        self.driver_to_cell: Dict[str, HexCell] = {}

    def lat_lng_to_cell(self, lat: float, lng: float) -> HexCell:
        # Simple equirectangular projection approximation for local cells
        x = lng * math.cos(math.radians(lat)) / self.resolution_step
        y = lat / self.resolution_step
        
        # Point to hex conversion (axial coordinates)
        q = (2.0/3.0 * x)
        r = (-1.0/3.0 * x + math.sqrt(3.0)/3.0 * y)
        
        return self._round_hex(q, r)

    def _round_hex(self, q: float, r: float) -> HexCell:
        s = -q - r
        q_round = round(q)
        r_round = round(r)
        s_round = round(s)
        
        q_diff = abs(q_round - q)
        r_diff = abs(r_round - r)
        s_diff = abs(s_round - s)
        
        if q_diff > r_diff and q_diff > s_diff:
            q_round = -r_round - s_round
        elif r_diff > s_diff:
            r_round = -q_round - s_round
            
        return HexCell(int(q_round), int(r_round))

    def get_k_ring(self, center: HexCell, k: int) -> List[HexCell]:
        results = []
        for dq in range(-k, k + 1):
            for dr in range(max(-k, -dq - k), min(k, -dq + k) + 1):
                results.append(HexCell(center.q + dq, center.r + dr))
        return results

    def update_driver_location(self, driver_id: str, lat: float, lng: float) -> None:
        cell = self.lat_lng_to_cell(lat, lng)
        old_cell = self.driver_to_cell.get(driver_id)
        
        if old_cell != cell:
            if old_cell:
                old_cell_str = str(old_cell)
                if old_cell_str in self.cell_to_drivers:
                    self.cell_to_drivers[old_cell_str].discard(driver_id)
            
            self.driver_to_cell[driver_id] = cell
            cell_str = str(cell)
            if cell_str not in self.cell_to_drivers:
                self.cell_to_drivers[cell_str] = set()
            self.cell_to_drivers[cell_str].add(driver_id)

    def find_drivers_in_k_ring(self, lat: float, lng: float, k: int) -> List[str]:
        center = self.lat_lng_to_cell(lat, lng)
        cells = self.get_k_ring(center, k)
        drivers = set()
        for cell in cells:
            cell_str = str(cell)
            if cell_str in self.cell_to_drivers:
                drivers.update(self.cell_to_drivers[cell_str])
        return list(drivers)
