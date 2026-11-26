import time
from multi_region.region_database import RegionDatabase
from multi_region.hybrid_logical_clock import HybridLogicalClock
from multi_region.record import Record

def test_basic_replication():
    us = RegionDatabase("US", ["EU", "APAC"])
    eu = RegionDatabase("EU", ["US", "APAC"])
    
    us.write("user1", "data-from-us")
    
    assert eu.read("user1") is None
    
    us.replicate_to(eu)
    
    record = eu.read("user1")
    assert record is not None
    assert record.data == "data-from-us"

def test_conflict_resolution_lww():
    us = RegionDatabase("US", ["EU"])
    eu = RegionDatabase("EU", ["US"])
    
    us.set_partitioned(True)
    eu.set_partitioned(True)
    
    us.write("user1", "data-from-us")
    time.sleep(0.01) # ensure physical time advances
    eu.write("user1", "data-from-eu")
    
    us.set_partitioned(False)
    eu.set_partitioned(False)
    
    us.replicate_to(eu)
    eu.replicate_to(us)
    
    assert us.read("user1").data == "data-from-eu"
    assert eu.read("user1").data == "data-from-eu"

def test_conflict_resolution_tiebreaker():
    us = RegionDatabase("US", ["EU"])
    eu = RegionDatabase("EU", ["US"])
    
    clock = HybridLogicalClock(1000, 0)
    record_us = Record("user1", "data-us", clock, "US")
    record_eu = Record("user1", "data-eu", clock, "EU")
    
    us.apply_replication(record_us)
    eu.apply_replication(record_eu)
    
    us.apply_replication(record_eu)
    eu.apply_replication(record_us)
    
    assert us.read("user1").data == "data-us"
    assert eu.read("user1").data == "data-us"
