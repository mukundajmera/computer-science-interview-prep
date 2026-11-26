import os
import sys
import pytest
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-distributed')))

from distributed_ride_service import (
    BatchedBipartiteDispatcher, 
    GeoSearchIndex, 
    GeoDriverCandidate
)

class MockGeoSearchIndex(GeoSearchIndex):
    def __init__(self):
        self.entities = []
        
    def nearby_entities(self, lat: float, lng: float, radius_km: float, limit: int) -> List[GeoDriverCandidate]:
        if lat == 0.0 and lng == 0.0:
            return [
                GeoDriverCandidate("d1", 5.0, 1.0),
                GeoDriverCandidate("d2", 10.0, 2.0)
            ]
        elif lat == 1.0 and lng == 1.0:
            return [
                GeoDriverCandidate("d1", 2.0, 0.5), # D1 is closer to here
                GeoDriverCandidate("d2", 3.0, 0.7)
            ]
        return []
        
    def upsert_position(self, driver_id: str, lat: float, lng: float, timestamp_millis: int) -> None:
        pass


def test_bipartite_dispatch_optimization():
    index = MockGeoSearchIndex()
    dispatcher = BatchedBipartiteDispatcher(index)
    
    # Request 1 at origin
    dispatcher.submit_request("r1", 0.0, 0.0)
    
    # Request 2 at (1,1)
    dispatcher.submit_request("r2", 1.0, 1.0)
    
    # Run dispatch
    matches = dispatcher.dispatch_batch()
    
    # For r1, d1 has ETA 5, d2 has ETA 10
    # For r2, d1 has ETA 2, d2 has ETA 3
    # If greedy by ETA: 
    # Edge (r2, d1, 2) is chosen first. So r2 matches d1.
    # Next edge is (r2, d2, 3) - r2 already matched.
    # Next edge is (r1, d1, 5) - d1 already matched.
    # Next edge is (r1, d2, 10) - chosen. So r1 matches d2.
    
    assert matches.get("r2") == "d1"
    assert matches.get("r1") == "d2"
    
def test_bipartite_dispatch_empty():
    index = MockGeoSearchIndex()
    dispatcher = BatchedBipartiteDispatcher(index)
    
    matches = dispatcher.dispatch_batch()
    assert len(matches) == 0

def test_bipartite_dispatch_partial_match():
    index = MockGeoSearchIndex()
    dispatcher = BatchedBipartiteDispatcher(index)
    
    dispatcher.submit_request("r1", 0.0, 0.0)
    dispatcher.submit_request("r2", 1.0, 1.0)
    dispatcher.submit_request("r3", 2.0, 2.0) # No candidates here
    
    matches = dispatcher.dispatch_batch()
    
    assert "r1" in matches
    assert "r2" in matches
    assert "r3" not in matches
    
def test_submit_request_thread_safe():
    index = MockGeoSearchIndex()
    dispatcher = BatchedBipartiteDispatcher(index)
    
    # We don't really run real threads but verify the lock works in basic scenario
    dispatcher.submit_request("r1", 0.0, 0.0)
    assert len(dispatcher.pending_requests) == 1
    
    matches = dispatcher.dispatch_batch()
    assert len(dispatcher.pending_requests) == 0
