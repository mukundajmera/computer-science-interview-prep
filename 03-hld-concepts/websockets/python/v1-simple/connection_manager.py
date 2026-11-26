"""Simple WebSocket-style connection manager simulation."""

from collections import defaultdict
from typing import DefaultDict, List


class ConnectionManager:
    def __init__(self):
        self._rooms: DefaultDict[str, List[str]] = defaultdict(list)

    def connect(self, room: str, client_id: str) -> None:
        if client_id not in self._rooms[room]:
            self._rooms[room].append(client_id)

    def disconnect(self, room: str, client_id: str) -> None:
        clients = self._rooms.get(room)
        if clients and client_id in clients:
            clients.remove(client_id)
            if not clients:
                del self._rooms[room]

    def broadcast_targets(self, room: str) -> List[str]:
        return list(self._rooms.get(room, []))


if __name__ == "__main__":
    manager = ConnectionManager()
    manager.connect("chat-1", "u1")
    manager.connect("chat-1", "u2")
    print(manager.broadcast_targets("chat-1"))
