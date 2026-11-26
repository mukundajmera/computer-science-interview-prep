import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'v1-basic')))

import pytest
import concurrent.futures
import itertools
from typing import Optional
from collaborative_editor_service import CollaborativeEditorService, CollaborativeEditorServiceImpl, Document, DocumentOperation, OperationAck

def test_create_document():
    service = CollaborativeEditorServiceImpl()
    doc = service.create_document("user-1", "Test Doc")
    
    assert doc.document_id == "doc-1"
    assert doc.owner_id == "user-1"
    assert doc.title == "Test Doc"
    assert doc.version == 0

def test_get_document():
    service = CollaborativeEditorServiceImpl()
    doc = service.create_document("user-1", "Test Doc")
    
    found_doc = service.get_document("doc-1", "user-1")
    assert found_doc is not None
    assert found_doc.document_id == "doc-1"
    
    not_found = service.get_document("doc-2", "user-1")
    assert not_found is None

def test_apply_operation():
    service = CollaborativeEditorServiceImpl()
    service.create_document("user-1", "Test Doc")
    
    op1 = DocumentOperation("op-1", 0, "INSERT 0 A")
    ack1 = service.apply_operation("doc-1", "user-1", op1)
    
    assert ack1.operation_id == "op-1"
    assert ack1.applied_version == 1
    assert ack1.rebased is False
    assert service.get_document_content("doc-1") == "A"
    
    # Concurrent insert at same index
    op2 = DocumentOperation("op-2", 0, "INSERT 0 B")
    ack2 = service.apply_operation("doc-1", "user-1", op2)
    assert ack2.rebased is True
    # Transform tie breaks by operation_id, op-2 > op-1, so op2 gets index 1
    assert service.get_document_content("doc-1") == "AB"

def test_permutation_convergence():
    # We want to test that arriving in different orders yields the same final string
    operations = [
        DocumentOperation("op-A", 0, "INSERT 0 H"),
        DocumentOperation("op-B", 0, "INSERT 0 E"),
        DocumentOperation("op-C", 0, "INSERT 0 L")
    ]
    
    results = set()
    
    for perm in itertools.permutations(operations):
        service = CollaborativeEditorServiceImpl()
        doc = service.create_document("u1", "test")
        
        for op in perm:
            service.apply_operation(doc.document_id, "u1", op)
            
        results.add(service.get_document_content(doc.document_id))
        
    # Since they are concurrent and tie broken by op id, they should all converge to the same
    # op-C > op-B > op-A lexicographically
    # They all insert at 0.
    # C wins over B and A, B wins over A.
    # So C goes to 2, B to 1, A to 0? Or A goes to 0, B to 1, C to 2?
    # As long as it converges to 1 unique result!
    assert len(results) == 1

def test_concurrent_edits_delete_insert():
    service = CollaborativeEditorServiceImpl()
    doc = service.create_document("u1", "test")
    
    # Initial setup: "AB"
    service.apply_operation(doc.document_id, "u1", DocumentOperation("op-1", 0, "INSERT 0 A"))
    service.apply_operation(doc.document_id, "u1", DocumentOperation("op-2", 1, "INSERT 1 B"))
    
    # Concurrent op3: DELETE 0 (deletes A)
    # Concurrent op4: INSERT 1 C (inserts C between A and B) -> base index 1
    
    # If op3 arrives first:
    # state: "B" (index 0 is B)
    # op4 arrives, base version is 2. Needs to transform against op3 (DELETE 0).
    # op4 is INSERT 1 C. Since idx1 (1) > idx2 (0), new_idx1 = 1 - 1 = 0.
    # op4 transformed: INSERT 0 C.
    # state becomes "CB"
    
    # Let's test arriving op3 then op4
    s1 = CollaborativeEditorServiceImpl()
    d1 = s1.create_document("u1", "t1")
    s1.apply_operation(d1.document_id, "u1", DocumentOperation("op-1", 0, "INSERT 0 A"))
    s1.apply_operation(d1.document_id, "u1", DocumentOperation("op-2", 1, "INSERT 1 B"))
    s1.apply_operation(d1.document_id, "u1", DocumentOperation("op-3", 2, "DELETE 0"))
    s1.apply_operation(d1.document_id, "u1", DocumentOperation("op-4", 2, "INSERT 1 C"))
    res1 = s1.get_document_content(d1.document_id)
    
    # Let's test arriving op4 then op3
    s2 = CollaborativeEditorServiceImpl()
    d2 = s2.create_document("u1", "t2")
    s2.apply_operation(d2.document_id, "u1", DocumentOperation("op-1", 0, "INSERT 0 A"))
    s2.apply_operation(d2.document_id, "u1", DocumentOperation("op-2", 1, "INSERT 1 B"))
    s2.apply_operation(d2.document_id, "u1", DocumentOperation("op-4", 2, "INSERT 1 C"))
    s2.apply_operation(d2.document_id, "u1", DocumentOperation("op-3", 2, "DELETE 0"))
    res2 = s2.get_document_content(d2.document_id)
    
    assert res1 == res2 == "CB"

def test_concurrent_edits_delete_delete():
    service = CollaborativeEditorServiceImpl()
    doc = service.create_document("u1", "t")
    service.apply_operation(doc.document_id, "u1", DocumentOperation("op-1", 0, "INSERT 0 A"))
    
    # Two people try to delete 'A'
    op2 = DocumentOperation("op-2", 1, "DELETE 0")
    op3 = DocumentOperation("op-3", 1, "DELETE 0")
    
    service.apply_operation(doc.document_id, "u1", op2)
    service.apply_operation(doc.document_id, "u1", op3)
    
    assert service.get_document_content(doc.document_id) == ""
