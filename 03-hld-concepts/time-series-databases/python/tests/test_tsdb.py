import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-blocks')))

from tsdb import TSDBEngine

def test_tsdb_insert_query():
    db = TSDBEngine()
    db.insert("cpu", 100, 1.0)
    db.insert("cpu", 200, 2.0)
    db.insert("cpu", 300, 3.0)
    
    assert db.range_query("cpu", 150, 350) == [(200, 2.0), (300, 3.0)]

def test_tsdb_cardinality():
    db = TSDBEngine(max_series=2)
    db.insert("cpu", 100, 1.0)
    db.insert("mem", 100, 1.0)
    
    with pytest.raises(ValueError, match="Cardinality limit reached"):
        db.insert("disk", 100, 1.0)

def test_tsdb_downsample():
    db = TSDBEngine()
    db.insert("cpu", 10, 1.0)
    db.insert("cpu", 15, 2.0)
    db.insert("cpu", 25, 3.0)
    db.insert("cpu", 35, 3.0)
    
    res = db.downsample("cpu", 20)
    # bucket 0: 10, 15 => avg 1.5
    # bucket 20: 25, 35 => avg 3.0
    assert res == [(0, 1.5), (20, 3.0)]

def test_tsdb_retention():
    db = TSDBEngine()
    db.insert("cpu", 100, 1.0)
    db.insert("cpu", 200, 2.0)
    
    db.apply_retention(150)
    assert db.range_query("cpu", 0, 1000) == [(200, 2.0)]
