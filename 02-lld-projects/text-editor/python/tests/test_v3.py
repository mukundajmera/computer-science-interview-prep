import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from gap_buffer import GapBuffer

def test_v3_gap_buffer_insert():
    gb = GapBuffer(initial_capacity=5)
    gb.insert(0, "Line 1")
    gb.insert(1, "Line 2")
    assert gb.get_all() == ["Line 1", "Line 2"]
    
def test_v3_gap_buffer_insert_middle():
    gb = GapBuffer(initial_capacity=5)
    gb.insert(0, "Line 1")
    gb.insert(1, "Line 3")
    gb.insert(1, "Line 2") # Insert between 1 and 3
    assert gb.get_all() == ["Line 1", "Line 2", "Line 3"]
    
def test_v3_gap_buffer_delete():
    gb = GapBuffer(initial_capacity=5)
    gb.insert(0, "A")
    gb.insert(1, "B")
    gb.insert(2, "C")
    gb.delete(1)
    assert gb.get_all() == ["A", "C"]
    
def test_v3_gap_buffer_replace():
    gb = GapBuffer(initial_capacity=5)
    gb.insert(0, "A")
    gb.insert(1, "B")
    gb.replace(1, "X")
    assert gb.get_all() == ["A", "X"]
    
def test_v3_gap_buffer_resize():
    gb = GapBuffer(initial_capacity=2)
    gb.insert(0, "A")
    gb.insert(1, "B")
    gb.insert(2, "C") # This will trigger resize
    assert gb.get_all() == ["A", "B", "C"]
