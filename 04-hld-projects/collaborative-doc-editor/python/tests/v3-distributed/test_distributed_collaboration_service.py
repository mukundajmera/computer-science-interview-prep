import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v3-distributed')))

import pytest
import itertools
from distributed_collaboration_service import DistributedCollaborationService, DistributedCollaborationServiceImpl, OperationReplicationEvent, StateVector

def test_route_document_owner():
    service = DistributedCollaborationServiceImpl("node-0")
    # Due to md5 hash, it will return some node consistently
    node1 = service.route_document_owner("doc-1")
    node2 = service.route_document_owner("doc-1")
    assert node1 == node2
    assert node1 in ["node-1", "node-2", "node-3", "node-default"]

def test_replicate_operation():
    service = DistributedCollaborationServiceImpl("node-1")
    
    # Event 1: node-2 sends an insert
    deps1 = StateVector({"node-2": 0})
    event1 = OperationReplicationEvent("doc-1", 1, "INSERT null null 1 u1 A", "node-2", 1, deps1)
    service.replicate_operation(event1)
    
    assert service.get_document_content("doc-1") == "A"
    
    # Event 2: node-2 sends a delete
    deps2 = StateVector({"node-2": 1})
    event2 = OperationReplicationEvent("doc-1", 2, "DELETE 1 u1", "node-2", 2, deps2)
    service.replicate_operation(event2)
    
    assert service.get_document_content("doc-1") == ""

def test_causal_broadcast_buffering():
    service = DistributedCollaborationServiceImpl("node-1")
    
    # We send event 2 before event 1 to simulate out-of-order delivery
    # Event 2 depends on Event 1 (node-2 seq 1)
    deps2 = StateVector({"node-2": 1})
    event2 = OperationReplicationEvent("doc-1", 2, "DELETE 1 u1", "node-2", 2, deps2)
    service.replicate_operation(event2)
    
    # The event is buffered because node-1's state vector for node-2 is 0, but deps require 1, 
    # and expected seq is 1, but got 2.
    # Content should remain empty as the document hasn't been instantiated properly or 
    # the delete hasn't been applied to anything
    assert service.get_document_content("doc-1") == ""
    
    # Event 1: node-2 seq 1
    deps1 = StateVector({"node-2": 0})
    event1 = OperationReplicationEvent("doc-1", 1, "INSERT null null 1 u1 A", "node-2", 1, deps1)
    service.replicate_operation(event1)
    
    # Now Event 1 unblocks Event 2.
    # Event 1 applies A, Event 2 applies Delete. 
    # So the final result should be empty, but let's check it doesn't crash and works correctly.
    assert service.get_document_content("doc-1") == ""

def test_tombstone_compaction():
    service = DistributedCollaborationServiceImpl("node-1")
    
    deps1 = StateVector({"node-2": 0})
    event1 = OperationReplicationEvent("doc-1", 1, "INSERT null null 1 u1 A", "node-2", 1, deps1)
    service.replicate_operation(event1)
    
    deps2 = StateVector({"node-2": 1})
    event2 = OperationReplicationEvent("doc-1", 2, "INSERT 1 u1 2 u2 B", "node-2", 2, deps2)
    service.replicate_operation(event2)
    
    assert service.get_document_content("doc-1") == "AB"
    
    deps3 = StateVector({"node-2": 2})
    event3 = OperationReplicationEvent("doc-1", 3, "DELETE 1 u1", "node-2", 3, deps3)
    service.replicate_operation(event3)
    
    # A is deleted
    assert service.get_document_content("doc-1") == "B"
    
    # Perform tombstone compaction
    service.compact_tombstones("doc-1")
    
    # B should still be there, but A's node is physically removed
    assert service.get_document_content("doc-1") == "B"
    
def test_permutation_convergence_causal():
    # If we have concurrent operations from different nodes, any order of arrival
    # should converge, as long as causal deps are respected per node.
    # Node 1 inserts A
    # Node 2 inserts B after A
    # Node 3 inserts C after A
    
    ops = [
        OperationReplicationEvent("doc-1", 1, "INSERT null null 1 n1 A", "node-1", 1, StateVector({})),
        OperationReplicationEvent("doc-1", 2, "INSERT 1 n1 2 n2 B", "node-2", 1, StateVector({"node-1": 1})),
        OperationReplicationEvent("doc-1", 3, "INSERT 1 n1 3 n3 C", "node-3", 1, StateVector({"node-1": 1}))
    ]
    
    results = set()
    for perm in itertools.permutations(ops):
        service = DistributedCollaborationServiceImpl("test-node")
        
        for op in perm:
            service.replicate_operation(op)
            
        results.add(service.get_document_content("doc-1"))
        
    assert len(results) == 1

