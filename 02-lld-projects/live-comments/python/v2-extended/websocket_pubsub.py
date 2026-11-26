from typing import Dict, Set, Protocol
import threading

class WebSocketConnection(Protocol):
    def send(self, payload: str) -> None: ...

class WebSocketSessionPubSub:
    def __init__(self):
        # stream_id -> set of session_ids
        self.stream_subscriptions: Dict[str, Set[str]] = {}
        self.active_connections: Dict[str, WebSocketConnection] = {}
        self.lock = threading.Lock()
        
    def add_connection(self, session_id: str, connection: WebSocketConnection) -> None:
        with self.lock:
            self.active_connections[session_id] = connection

    def register(self, stream_id: str, session_id: str, user_id: str) -> None:
        with self.lock:
            if stream_id not in self.stream_subscriptions:
                self.stream_subscriptions[stream_id] = set()
            self.stream_subscriptions[stream_id].add(session_id)

    def unregister(self, stream_id: str, session_id: str) -> None:
        with self.lock:
            if stream_id in self.stream_subscriptions:
                self.stream_subscriptions[stream_id].discard(session_id)
                if not self.stream_subscriptions[stream_id]:
                    del self.stream_subscriptions[stream_id]
            self.active_connections.pop(session_id, None)

    def fanout(self, stream_id: str, comment_payload: str, event_time_ms: int) -> None:
        with self.lock:
            sessions = self.stream_subscriptions.get(stream_id, set()).copy()
            conns = [self.active_connections.get(sid) for sid in sessions]
            
        for conn in conns:
            if conn is not None:
                try:
                    conn.send(comment_payload)
                except Exception:
                    # ensure subscriber disconnect cannot block unrelated subscribers indefinitely
                    continue
