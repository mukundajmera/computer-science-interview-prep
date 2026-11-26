import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v2-scaled')))

import pytest
import itertools
from typing import List
from document_session_service import DocumentSessionService, DocumentSessionServiceImpl, InMemoryOperationLogStore, SessionToken, OperationLogStore, OperationEvent, RGANodeID

def test_join_session():
    store = InMemoryOperationLogStore()
    service = DocumentSessionServiceImpl(store)
    
    token = service.join_session("doc-1", "user-1", 10)
    
    assert token.document_id == "doc-1"
    assert token.user_id == "user-1"
    assert token.stream_offset == 10

def test_publish_and_leave_session():
    store = InMemoryOperationLogStore()
    service = DocumentSessionServiceImpl(store)
    service.join_session("doc-1", "user-1", 0)
    service.publish_cursor("doc-1", "user-1", 5)
    service.leave_session("doc-1", "user-1")
    assert True

def test_operation_log_store():
    store = InMemoryOperationLogStore()
    store.append(OperationEvent(1, "doc-1", "payload-1"))
    store.append(OperationEvent(2, "doc-1", "payload-2"))
    store.append(OperationEvent(3, "doc-2", "payload-3"))
    
    replays = store.replay("doc-1", 1, 10)
    assert len(replays) == 1
    assert replays[0].operation_id == 2
    assert replays[0].payload == "payload-2"

def test_crdt_insert_and_delete():
    store = InMemoryOperationLogStore()
    service = DocumentSessionServiceImpl(store)
    
    # INSERT null null 1 u1 A -> prev=none, ts=1, client=u1, val=A
    op1 = OperationEvent(1, "doc-1", "INSERT null null 1 u1 A")
    service.apply_crdt_operation(op1)
    
    assert service.get_document_content("doc-1") == "A"
    
    # INSERT 1 u1 2 u2 B -> prev=(1,u1), ts=2, client=u2, val=B
    op2 = OperationEvent(2, "doc-1", "INSERT 1 u1 2 u2 B")
    service.apply_crdt_operation(op2)
    
    assert service.get_document_content("doc-1") == "AB"
    
    # DELETE 1 u1
    op3 = OperationEvent(3, "doc-1", "DELETE 1 u1")
    service.apply_crdt_operation(op3)
    
    assert service.get_document_content("doc-1") == "B"

def test_crdt_concurrent_inserts():
    # Two inserts after the same character
    # Initial: A (1, u1)
    # C1 inserts B at (2, c1) after A
    # C2 inserts C at (2, c2) after A
    # RGA orders by timestamp descending, then client_id descending?
    # Wait, in RGA, if ts > new_ts, skip.
    # So the one with larger ID will appear FIRST (to the left).
    # ID comparison: __lt__ does ts < ts or (ts == ts and client < client)
    # So if C2 > C1, C2 appears before C1.
    
    store1 = InMemoryOperationLogStore()
    s1 = DocumentSessionServiceImpl(store1)
    s1.apply_crdt_operation(OperationEvent(1, "doc-1", "INSERT null null 1 u0 A"))
    # C1 then C2
    s1.apply_crdt_operation(OperationEvent(2, "doc-1", "INSERT 1 u0 2 c1 B"))
    s1.apply_crdt_operation(OperationEvent(3, "doc-1", "INSERT 1 u0 2 c2 C"))
    res1 = s1.get_document_content("doc-1")
    
    store2 = InMemoryOperationLogStore()
    s2 = DocumentSessionServiceImpl(store2)
    s2.apply_crdt_operation(OperationEvent(1, "doc-1", "INSERT null null 1 u0 A"))
    # C2 then C1
    s2.apply_crdt_operation(OperationEvent(3, "doc-1", "INSERT 1 u0 2 c2 C"))
    s2.apply_crdt_operation(OperationEvent(2, "doc-1", "INSERT 1 u0 2 c1 B"))
    res2 = s2.get_document_content("doc-1")
    
    assert res1 == res2
    # c2 > c1, so c2 is skipped by c1? Let's trace.
    # In RGA: curr.node_id > new_node_id -> skip
    # For c1 (new): is c2 > c1? Yes. So c1 skips c2. c1 is inserted after c2.
    # Result should be A, c2, c1 -> A C B.
    assert res1 == "ACB"

def test_permutation_convergence():
    ops = [
        OperationEvent(2, "doc-1", "INSERT 1 u0 2 c1 B"),
        OperationEvent(3, "doc-1", "INSERT 1 u0 3 c2 C"),
        OperationEvent(4, "doc-1", "INSERT 1 u0 2 c3 D")
    ]
    
    results = set()
    for perm in itertools.permutations(ops):
        store = InMemoryOperationLogStore()
        s = DocumentSessionServiceImpl(store)
        
        # Base setup
        s.apply_crdt_operation(OperationEvent(1, "doc-1", "INSERT null null 1 u0 A"))
        
        for op in perm:
            s.apply_crdt_operation(op)
            
        results.add(s.get_document_content("doc-1"))
        
    assert len(results) == 1

