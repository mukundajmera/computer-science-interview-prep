import pytest
import sys
import os

# Adjust sys.path to import the module properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from causal_clock_engine import LamportClock, VectorClock, TrueTimeSimulator, Causality

def test_lamport_monotonicity_and_ordering():
    node_a = LamportClock("A")
    node_b = LamportClock("B")

    # Local events
    time_a1 = node_a.tick() # 1
    assert time_a1 == 1

    time_b1 = node_b.tick() # 1
    assert time_b1 == 1

    # Send message A -> B
    time_a2 = node_a.send_event() # 2
    time_b2 = node_b.receive_event(time_a2) # max(1, 2) + 1 = 3
    
    assert time_b2 == 3
    assert LamportClock.compare_causality(time_a2, "A", time_b2, "B") == Causality.BEFORE

    # Tiebreaker test
    assert LamportClock.compare_causality(3, "A", 3, "B") == Causality.BEFORE
    assert LamportClock.compare_causality(3, "B", 3, "A") == Causality.AFTER

def test_vector_clock_causal_ordering():
    node_a = VectorClock("A")
    node_b = VectorClock("B")

    v_a1 = node_a.tick() # A: [1]
    assert v_a1 == {"A": 1}

    v_a2 = node_a.send_event() # A: [2]
    v_b1 = node_b.receive_event(v_a2) # B: A:2, B:1
    assert v_b1 == {"A": 2, "B": 1}

    assert VectorClock.compare_causality(v_a2, v_b1) == Causality.BEFORE

def test_vector_clock_concurrent_conflict():
    node_a = VectorClock("A")
    node_b = VectorClock("B")

    v_a1 = node_a.tick() # A: [1]
    v_b1 = node_b.tick() # B: [1]

    # Concurrent events, neither knows about the other
    assert VectorClock.compare_causality(v_a1, v_b1) == Causality.CONCURRENT

    # A sends to B
    v_a2 = node_a.send_event() # A: [2]
    v_b2 = node_b.receive_event(v_a2) # B: A:2, B:2

    # B ticks again
    v_b3 = node_b.tick() # B: A:2, B:3

    # C gets A1, and D gets B3, test them
    node_c = VectorClock("C")
    v_c1 = node_c.receive_event(v_a1) # C: A:1, C:1

    node_d = VectorClock("D")
    v_d1 = node_d.receive_event(v_b3) # D: A:2, B:3, D:1

    # C knows A1, D knows A2, B3. D > C is false because C has C:1 which D does not. D and C are concurrent.
    assert VectorClock.compare_causality(v_c1, v_d1) == Causality.CONCURRENT


def test_truetime_commit_wait():
    tt = TrueTimeSimulator(epsilon_ms=5)

    # Transaction 1
    t1_commit_ts = tt.commit_transaction()

    # Get now immediately after T1 completes
    earliest, latest = tt.now()

    # The TrueTime commit wait guarantees that TT.now().earliest > commit_timestamp
    assert earliest > t1_commit_ts

    # Transaction 2
    t2_commit_ts = tt.commit_transaction()

    assert t2_commit_ts > t1_commit_ts
