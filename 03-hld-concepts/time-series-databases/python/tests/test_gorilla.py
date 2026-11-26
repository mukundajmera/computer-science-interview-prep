import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-compression')))

from gorilla import GorillaCompressor, GorillaDecompressor, CompressedSeries

def test_gorilla_roundtrip():
    c = GorillaCompressor()
    timestamps = [1600000000, 1600000015, 1600000030, 1600000046, 1600000060, 1600000075]
    for t in timestamps:
        c.add_timestamp(t)

    d = GorillaDecompressor(c.writer.bits)
    res = d.read_timestamp(len(timestamps))
    
    assert res == timestamps
    
def test_compressed_series_range_query():
    series = CompressedSeries()
    timestamps = [100, 115, 130, 145, 160]
    for t in timestamps:
        series.add(t)
        
    res = series.range_query(120, 150)
    assert res == [130, 145]
