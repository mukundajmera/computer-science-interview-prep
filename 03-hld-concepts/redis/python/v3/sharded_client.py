from __future__ import annotations

import binascii
from typing import Any, Dict, Optional, Tuple

class Node:
    def __init__(self, node_id: str, host: str, port: int):
        self.node_id = node_id
        self.host = host
        self.port = port
        self.store: Dict[str, Any] = {}
        # Node knows its assigned slots
        self.assigned_slots = set()
        
    def get(self, key: str) -> Optional[Any]:
        return self.store.get(key)
        
    def set(self, key: str, value: Any) -> None:
        self.store[key] = value
        
    def delete(self, key: str) -> None:
        self.store.pop(key, None)

class ShardedClient:
    def __init__(self, nodes: list[Node]):
        self.nodes = {n.node_id: n for n in nodes}
        self.slots = [None] * 16384
        self._assign_slots()
        
        # Hot key cache
        self.local_cache: Dict[str, Any] = {}
        self.access_counts: Dict[str, int] = {}
        self.HOT_KEY_THRESHOLD = 5
        
    def _assign_slots(self):
        node_ids = list(self.nodes.keys())
        num_nodes = len(node_ids)
        for i in range(16384):
            node_id = node_ids[i % num_nodes]
            self.slots[i] = node_id
            self.nodes[node_id].assigned_slots.add(i)
            
    def _get_hash_slot(self, key: str) -> int:
        hash_tag_start = key.find('{')
        hash_tag_end = key.find('}', hash_tag_start + 1)
        if hash_tag_start != -1 and hash_tag_end != -1:
            key_to_hash = key[hash_tag_start + 1:hash_tag_end]
        else:
            key_to_hash = key
            
        # Proper CRC16 calculation is complex in standard library, 
        # but we use crc32 % 16384 for demonstration of sharding
        return binascii.crc32(key_to_hash.encode()) % 16384
        
    def execute_command(self, command: str, key: str, value: Any = None, initial_node_id: str = None) -> Tuple[Optional[Any], Optional[str]]:
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        
        if command == "GET" and key in self.local_cache:
            return self.local_cache[key], None

        slot = self._get_hash_slot(key)
        correct_node_id = self.slots[slot]
        correct_node = self.nodes[correct_node_id]
        
        # Simulate hitting a random node or stale cache
        contacted_node_id = initial_node_id if initial_node_id else correct_node_id
        contacted_node = self.nodes[contacted_node_id]
        
        if slot not in contacted_node.assigned_slots:
            return None, f"MOVED {slot} {correct_node.host}:{correct_node.port}"
        
        if self.access_counts[key] > self.HOT_KEY_THRESHOLD and command == "GET":
            val = correct_node.get(key)
            self.local_cache[key] = val
            return val, None
            
        if command == "GET":
            return correct_node.get(key), None
        elif command == "SET":
            correct_node.set(key, value)
            if key in self.local_cache:
                self.local_cache[key] = value
            return "OK", None
        return None, "UNKNOWN_COMMAND"
