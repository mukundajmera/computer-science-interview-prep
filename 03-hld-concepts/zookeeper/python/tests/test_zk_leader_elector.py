import sys
import os
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-simple')))

from zk_leader_elector import ZkSimulator, ZkLeaderElector

def test_single_node_becomes_leader():
    zk = ZkSimulator()
    elector = ZkLeaderElector(zk, "/election", "session_1")

    leadership_events = []
    elector.on_leadership_change = lambda is_leader: leadership_events.append(is_leader)

    elector.join_election()

    assert elector.is_leader is True
    assert leadership_events == [True]

def test_multiple_nodes_election():
    zk = ZkSimulator()
    elector1 = ZkLeaderElector(zk, "/election", "session_1")
    elector2 = ZkLeaderElector(zk, "/election", "session_2")
    elector3 = ZkLeaderElector(zk, "/election", "session_3")

    elector1.join_election()
    elector2.join_election()
    elector3.join_election()

    # Only the first one should be leader
    assert elector1.is_leader is True
    assert elector2.is_leader is False
    assert elector3.is_leader is False

    # Elector 2 should be watching Elector 1's node
    # Elector 3 should be watching Elector 2's node
    node1_path = elector1.node_path
    node2_path = elector2.node_path

    assert node1_path in zk.watches
    assert len(zk.watches[node1_path]) == 1

    assert node2_path in zk.watches
    assert len(zk.watches[node2_path]) == 1

def test_leader_failover():
    zk = ZkSimulator()
    elector1 = ZkLeaderElector(zk, "/election", "session_1")
    elector2 = ZkLeaderElector(zk, "/election", "session_2")

    elector1.join_election()
    elector2.join_election()

    assert elector1.is_leader is True
    assert elector2.is_leader is False

    # Simulate session 1 expiration
    zk.expire_session("session_1")

    # Elector 2 should be notified and become leader
    assert elector2.is_leader is True

def test_thundering_herd_prevention():
    # If the leader fails, only the node right behind it should be triggered,
    # not all nodes.
    zk = ZkSimulator()
    electors = []

    for i in range(5):
        elector = ZkLeaderElector(zk, "/election", f"session_{i}")
        electors.append(elector)
        elector.join_election()

    assert electors[0].is_leader is True
    for i in range(1, 5):
        assert electors[i].is_leader is False

    # Check watches setup: e[i] watches e[i-1]
    for i in range(1, 5):
        watched_path = electors[i-1].node_path
        assert len(zk.watches.get(watched_path, [])) == 1

    # Simulate session 0 expiration
    zk.expire_session("session_0")

    # elector 1 should become leader
    assert electors[1].is_leader is True
    # others should still not be leader
    for i in range(2, 5):
        assert electors[i].is_leader is False
