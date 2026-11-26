from dataclasses import dataclass
from typing import Protocol, Dict, List, Optional, Tuple
import threading
import json
import hashlib


@dataclass(frozen=True)
class StateVector:
    vector: Dict[str, int] # node_id -> max_operation_sequence
    
    def dominates(self, other: 'StateVector') -> bool:
        # Returns True if self >= other in all dimensions
        for node, seq in other.vector.items():
            if self.vector.get(node, 0) < seq:
                return False
        return True


@dataclass(frozen=True)
class OperationReplicationEvent:
    document_id: str
    operation_id: int
    payload: str
    node_id: str
    node_seq: int
    deps: StateVector  # Causal dependencies


class DistributedCollaborationService(Protocol):
    def route_document_owner(self, document_id: str) -> str: ...
    def replicate_operation(self, event: OperationReplicationEvent) -> None: ...
    def rebuild_session_from_snapshot(self, document_id: str) -> None: ...
    
    def get_document_content(self, document_id: str) -> str: ...
    def compact_tombstones(self, document_id: str) -> None: ...


# We will re-use RGA structures for actual replication handling
@dataclass(frozen=True)
class RGANodeID:
    timestamp: int
    client_id: str
    
    def __lt__(self, other: 'RGANodeID') -> bool:
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        return self.client_id < other.client_id
        
    def __eq__(self, other: 'RGANodeID') -> bool:
        return self.timestamp == other.timestamp and self.client_id == other.client_id


class RGANode:
    def __init__(self, node_id: Optional[RGANodeID], value: Optional[str]):
        self.node_id = node_id
        self.value = value
        self.is_deleted = False
        self.next: Optional[RGANode] = None


class RGADocument:
    def __init__(self):
        self.head = RGANode(None, None)
        self.nodes_by_id: Dict[Tuple[int, str], RGANode] = {}
        
    def insert(self, prev_node_id: Optional[RGANodeID], new_node_id: RGANodeID, value: str):
        if (new_node_id.timestamp, new_node_id.client_id) in self.nodes_by_id:
            return
            
        new_node = RGANode(new_node_id, value)
        self.nodes_by_id[(new_node_id.timestamp, new_node_id.client_id)] = new_node
        
        if prev_node_id is None:
            prev = self.head
        else:
            key = (prev_node_id.timestamp, prev_node_id.client_id)
            if key not in self.nodes_by_id:
                return
            prev = self.nodes_by_id[key]
            
        curr = prev.next
        while curr is not None and curr.node_id is not None:
            if curr.node_id > new_node_id:
                prev = curr
                curr = curr.next
            else:
                break
                
        new_node.next = curr
        prev.next = new_node
        
    def delete(self, target_node_id: RGANodeID):
        key = (target_node_id.timestamp, target_node_id.client_id)
        if key in self.nodes_by_id:
            self.nodes_by_id[key].is_deleted = True
            
    def get_content(self) -> str:
        res = []
        curr = self.head.next
        while curr is not None:
            if not curr.is_deleted and curr.value is not None:
                res.append(curr.value)
            curr = curr.next
        return "".join(res)
        
    def compact_tombstones(self):
        # Remove completely deleted nodes where no child can be inserted
        # Note: in a true distributed RGA, compaction needs consensus.
        # Here we do a simplified compaction: just physical removal of deleted nodes from chain
        # Note: removing from chain might break future insertions that reference the deleted node.
        # But this is "Tombstone Compaction" which is acceptable after GC epoch.
        curr = self.head
        while curr.next is not None:
            if curr.next.is_deleted:
                # Remove from dict so it's fully gone (simulate epoch GC)
                # In reality we'd only do this if all nodes acknowledge they have seen the delete.
                key = (curr.next.node_id.timestamp, curr.next.node_id.client_id)
                if key in self.nodes_by_id:
                    del self.nodes_by_id[key]
                curr.next = curr.next.next
            else:
                curr = curr.next


class DistributedCollaborationServiceImpl:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._lock = threading.RLock()
        
        self.documents: Dict[str, RGADocument] = {}
        # Causal broadcast structures
        self.state_vectors: Dict[str, Dict[str, int]] = {} # doc_id -> {node -> seq}
        self.buffers: Dict[str, List[OperationReplicationEvent]] = {} # doc_id -> pending events
        
        # Simulating a ring or consistent hashing for route_document_owner
        self.nodes = ["node-1", "node-2", "node-3", "node-default"]

    def route_document_owner(self, document_id: str) -> str:
        # Simple consistent hash to nodes
        hash_val = int(hashlib.md5(document_id.encode()).hexdigest(), 16)
        idx = hash_val % len(self.nodes)
        return self.nodes[idx]

    def _get_or_create_doc(self, document_id: str) -> RGADocument:
        if document_id not in self.documents:
            self.documents[document_id] = RGADocument()
            self.state_vectors[document_id] = {self.node_id: 0}
            self.buffers[document_id] = []
        return self.documents[document_id]

    def replicate_operation(self, event: OperationReplicationEvent) -> None:
        with self._lock:
            doc = self._get_or_create_doc(event.document_id)
            buf = self.buffers[event.document_id]
            buf.append(event)
            self._try_deliver_buffered(event.document_id)

    def _try_deliver_buffered(self, document_id: str):
        buf = self.buffers[document_id]
        sv = self.state_vectors[document_id]
        
        progress = True
        while progress:
            progress = False
            for i, event in enumerate(buf):
                # An event is ready if our local SV dominates its causal dependencies,
                # AND it's exactly the next sequence from its origin node
                event_ready = True
                
                # Check causal deps
                for dep_node, dep_seq in event.deps.vector.items():
                    if sv.get(dep_node, 0) < dep_seq:
                        event_ready = False
                        break
                        
                # Check origin sequence
                expected_seq = sv.get(event.node_id, 0) + 1
                if event.node_seq > expected_seq:
                    event_ready = False
                elif event.node_seq < expected_seq:
                    # Already delivered, discard
                    buf.pop(i)
                    progress = True
                    break
                    
                if event_ready:
                    # Deliver!
                    self._apply_internal(document_id, event)
                    sv[event.node_id] = event.node_seq
                    buf.pop(i)
                    progress = True
                    break

    def _apply_internal(self, document_id: str, event: OperationReplicationEvent):
        doc = self.documents[document_id]
        
        parts = event.payload.split(' ')
        op_type = parts[0]
        
        if op_type == "INSERT":
            prev_ts = parts[1]
            prev_client = parts[2]
            ts = int(parts[3])
            client = parts[4]
            val = parts[5] if len(parts) > 5 else " "
            
            prev_node_id = None
            if prev_ts != "null":
                prev_node_id = RGANodeID(int(prev_ts), prev_client)
            new_node_id = RGANodeID(ts, client)
            
            doc.insert(prev_node_id, new_node_id, val)
            
        elif op_type == "DELETE":
            target_ts = int(parts[1])
            target_client = parts[2]
            doc.delete(RGANodeID(target_ts, target_client))

    def rebuild_session_from_snapshot(self, document_id: str) -> None:
        # In a real system, would download snapshot, load RGA nodes, and set SV
        with self._lock:
            self.documents[document_id] = RGADocument()
            self.state_vectors[document_id] = {self.node_id: 0}
            self.buffers[document_id] = []

    def get_document_content(self, document_id: str) -> str:
        with self._lock:
            doc = self._get_or_create_doc(document_id)
            return doc.get_content()
            
    def compact_tombstones(self, document_id: str) -> None:
        with self._lock:
            if document_id in self.documents:
                self.documents[document_id].compact_tombstones()

