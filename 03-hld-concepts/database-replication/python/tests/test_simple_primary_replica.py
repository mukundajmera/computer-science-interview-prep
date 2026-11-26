import os
import sys
import pytest

# Add v1_simple to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from simple_primary_replica import SimplePrimaryReplica

def test_write_and_read_from_replica():
    # Initialize with 3 replicas
    db = SimplePrimaryReplica(replica_count=3)

    # Write data
    db.write("key1", "value1")

    # Read should return from a replica
    value = db.read("key1")
    assert value == "value1"

def test_read_from_primary_consistency():
    db = SimplePrimaryReplica(replica_count=2)
    db.write("key2", "value2")

    # Read from primary
    value = db.read_from_primary("key2")
    assert value == "value2"

def test_zero_replicas_fallback():
    # If initialized with 0 replicas
    db = SimplePrimaryReplica(replica_count=0)
    db.write("key3", "value3")

    # read() should fallback to primary
    value = db.read("key3")
    assert value == "value3"
