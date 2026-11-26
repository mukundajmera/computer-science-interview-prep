from dataclasses import dataclass
from typing import List, Protocol, Dict, Optional, Tuple
import threading
import uuid


@dataclass(frozen=True)
class SessionToken:
    document_id: str
    user_id: str
    stream_offset: int


@dataclass(frozen=True)
class OperationEvent:
    operation_id: int
    document_id: str
    payload: str  # JSON-like string for RGA CRDT operations


class DocumentSessionService(Protocol):
    def join_session(self, document_id: str, user_id: str, last_seen_operation_id: int) -> SessionToken: ...
    def publish_cursor(self, document_id: str, user_id: str, position: int) -> None: ...
    def leave_session(self, document_id: str, user_id: str) -> None: ...
    
    # We will also expose CRDT operation interface here for our tests
    def apply_crdt_operation(self, event: OperationEvent) -> None: ...
    def get_document_content(self, document_id: str) -> str: ...


class OperationLogStore(Protocol):
    def append(self, event: OperationEvent) -> None: ...
    def replay(self, document_id: str, after_operation_id: int, limit: int) -> List[OperationEvent]: ...


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
        # The head is a dummy node representing the start of the document
        self.head = RGANode(None, None)
        self.nodes_by_id: Dict[Tuple[int, str], RGANode] = {}
        
    def insert(self, prev_node_id: Optional[RGANodeID], new_node_id: RGANodeID, value: str):
        if (new_node_id.timestamp, new_node_id.client_id) in self.nodes_by_id:
            return # Already inserted
            
        new_node = RGANode(new_node_id, value)
        self.nodes_by_id[(new_node_id.timestamp, new_node_id.client_id)] = new_node
        
        # Find prev node
        if prev_node_id is None:
            prev = self.head
        else:
            key = (prev_node_id.timestamp, prev_node_id.client_id)
            if key not in self.nodes_by_id:
                # In a real distributed system, we would buffer this until prev_node arrives.
                # For basic CRDT test cases, we assume causal delivery or we just append to head for now.
                # Let's handle it by returning if causal dependency is missing (simplified).
                return
            prev = self.nodes_by_id[key]
            
        # RGA insert logic
        # Find the correct position by skipping over nodes with timestamp > new_node.timestamp
        # or (timestamp == new_node.timestamp and client_id > new_node.client_id)
        
        curr = prev.next
        while curr is not None and curr.node_id is not None:
            # If the current node was inserted concurrently and has a higher ID, we skip it
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


class InMemoryOperationLogStore:
    def __init__(self):
        self._lock = threading.RLock()
        self.events: List[OperationEvent] = []

    def append(self, event: OperationEvent) -> None:
        with self._lock:
            self.events.append(event)

    def replay(self, document_id: str, after_operation_id: int, limit: int) -> List[OperationEvent]:
        with self._lock:
            result = []
            for e in self.events:
                if e.document_id == document_id and e.operation_id > after_operation_id:
                    result.append(e)
                    if len(result) >= limit:
                        break
            return result


class DocumentSessionServiceImpl:
    def __init__(self, log_store: OperationLogStore):
        self._lock = threading.RLock()
        self.log_store = log_store
        self.documents: Dict[str, RGADocument] = {}
        self.sessions: Dict[str, Dict[str, SessionToken]] = {} # doc_id -> user_id -> SessionToken

    def _get_or_create_doc(self, document_id: str) -> RGADocument:
        if document_id not in self.documents:
            self.documents[document_id] = RGADocument()
        return self.documents[document_id]

    def join_session(self, document_id: str, user_id: str, last_seen_operation_id: int) -> SessionToken:
        with self._lock:
            if document_id not in self.sessions:
                self.sessions[document_id] = {}
            
            # Replay missing operations
            missing_ops = self.log_store.replay(document_id, last_seen_operation_id, limit=1000)
            latest_op_id = last_seen_operation_id
            for op in missing_ops:
                self._apply_internal(op)
                latest_op_id = max(latest_op_id, op.operation_id)
                
            token = SessionToken(document_id, user_id, latest_op_id)
            self.sessions[document_id][user_id] = token
            return token

    def publish_cursor(self, document_id: str, user_id: str, position: int) -> None:
        pass

    def leave_session(self, document_id: str, user_id: str) -> None:
        with self._lock:
            if document_id in self.sessions and user_id in self.sessions[document_id]:
                del self.sessions[document_id][user_id]

    def _apply_internal(self, event: OperationEvent):
        doc = self._get_or_create_doc(event.document_id)
        
        # payload format: 
        # "INSERT prev_ts prev_client ts client val"
        # "DELETE target_ts target_client"
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

    def apply_crdt_operation(self, event: OperationEvent) -> None:
        with self._lock:
            self.log_store.append(event)
            self._apply_internal(event)
            
            # Update all active sessions
            if event.document_id in self.sessions:
                for user_id, token in self.sessions[event.document_id].items():
                    self.sessions[event.document_id][user_id] = SessionToken(
                        token.document_id, token.user_id, max(token.stream_offset, event.operation_id)
                    )

    def get_document_content(self, document_id: str) -> str:
        with self._lock:
            doc = self._get_or_create_doc(document_id)
            return doc.get_content()

