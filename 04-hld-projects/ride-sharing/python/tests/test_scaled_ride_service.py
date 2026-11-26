import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-scaled')))

from scaled_ride_service import H3SpatialIndexer, HexCell

def test_lat_lng_to_cell():
    indexer = H3SpatialIndexer(resolution_step=0.01)
    # Origin
    cell1 = indexer.lat_lng_to_cell(0.0, 0.0)
    assert cell1 == HexCell(0, 0)
    
    # Slight movement, same cell
    cell2 = indexer.lat_lng_to_cell(0.001, 0.001)
    assert cell1 == cell2
    
    # Far enough to be another cell
    cell3 = indexer.lat_lng_to_cell(0.05, 0.05)
    assert cell3 != cell1

def test_get_k_ring():
    indexer = H3SpatialIndexer()
    center = HexCell(0, 0)
    
    # k=0 should return just the center
    k0 = indexer.get_k_ring(center, 0)
    assert len(k0) == 1
    assert center in k0
    
    # k=1 should return 7 cells
    k1 = indexer.get_k_ring(center, 1)
    assert len(k1) == 7
    
    # k=2 should return 19 cells
    k2 = indexer.get_k_ring(center, 2)
    assert len(k2) == 19

def test_update_and_find_drivers():
    indexer = H3SpatialIndexer()
    
    # Add a driver at the origin
    indexer.update_driver_location("driver1", 0.0, 0.0)
    
    # Add another driver slightly away but within k=1
    indexer.update_driver_location("driver2", 0.01, 0.01)
    
    # Add a far driver
    indexer.update_driver_location("driver3", 0.1, 0.1)
    
    # Find at origin k=0
    drivers_k0 = indexer.find_drivers_in_k_ring(0.0, 0.0, 0)
    assert "driver1" in drivers_k0
    assert "driver3" not in drivers_k0
    
    # Find at origin k=1
    # Both driver1 and driver2 should be close
    drivers_k1 = indexer.find_drivers_in_k_ring(0.0, 0.0, 2)
    assert "driver1" in drivers_k1
    assert "driver2" in drivers_k1
    assert "driver3" not in drivers_k1
    
    # Move driver1 far away
    indexer.update_driver_location("driver1", 0.1, 0.1)
    drivers_k1_after = indexer.find_drivers_in_k_ring(0.0, 0.0, 2)
    assert "driver1" not in drivers_k1_after
    assert "driver2" in drivers_k1_after
