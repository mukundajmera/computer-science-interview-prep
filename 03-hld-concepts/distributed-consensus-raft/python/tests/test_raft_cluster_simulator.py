import pytest
import sys
import os

# Adjust sys.path to be able to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from raft_cluster_simulator import RaftClusterSimulator, NodeState

def test_leader_election():
    simulator = RaftClusterSimulator(5)
    
    # Node 0 starts election and wins
    success = simulator.start_election(0)
    assert success is True
    assert simulator.nodes[0].state == NodeState.LEADER
    assert simulator.nodes[0].current_term == 1
    
    # Check others are followers
    for i in range(1, 5):
        assert simulator.nodes[i].state == NodeState.FOLLOWER
        assert simulator.nodes[i].current_term == 1

def test_log_replication_quorum():
    simulator = RaftClusterSimulator(5)
    
    simulator.start_election(0)
    
    # Append command
    success = simulator.append_command(0, "SET x 10")
    assert success is True
    
    # Check that it is committed
    assert simulator.nodes[0].commit_index == 0
    assert len(simulator.nodes[0].log) == 1
    assert simulator.nodes[0].log[0].command == "SET x 10"
    
    # Verify replication
    for i in range(1, 5):
        assert simulator.nodes[i].commit_index == 0
        assert len(simulator.nodes[i].log) == 1
        assert simulator.nodes[i].log[0].command == "SET x 10"

def test_rejection_when_partitioned():
    simulator = RaftClusterSimulator(5)
    
    simulator.start_election(0)
    
    # Partition majority
    simulator.partition_node(2)
    simulator.partition_node(3)
    simulator.partition_node(4)
    
    # Append command, should fail as it can't reach quorum
    success = simulator.append_command(0, "SET y 20")
    assert success is False
    
    # Check that it is NOT committed
    assert simulator.nodes[0].commit_index == -1
    
    # Heal partition and retry
    simulator.heal_partition(2)
    simulator.heal_partition(3)
    simulator.heal_partition(4)
    
    success = simulator.append_command(0, "SET y 20")
    assert success is True
    # The first failed append added an entry, so commit index is 1 now.
    assert simulator.nodes[0].commit_index == 1

def test_log_reconciliation():
    simulator = RaftClusterSimulator(5)
    
    simulator.start_election(0)
    
    # Partition node 4
    simulator.partition_node(4)
    
    # Append commands to majority
    simulator.append_command(0, "cmd1")
    simulator.append_command(0, "cmd2")
    
    # Verify majority got them
    assert simulator.nodes[0].commit_index == 1
    assert simulator.nodes[1].commit_index == 1
    assert simulator.nodes[4].commit_index == -1 # Still behind
    assert len(simulator.nodes[4].log) == 0
    
    # Heal node 4
    simulator.heal_partition(4)
    
    # Next command will reconcile node 4
    simulator.append_command(0, "cmd3")
    
    assert simulator.nodes[4].commit_index == 2
    assert len(simulator.nodes[4].log) == 3
    assert simulator.nodes[4].log[0].command == "cmd1"
    assert simulator.nodes[4].log[1].command == "cmd2"
    assert simulator.nodes[4].log[2].command == "cmd3"
