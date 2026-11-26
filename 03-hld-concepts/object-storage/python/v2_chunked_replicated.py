import hashlib
from typing import List, Dict

class V2ChunkedReplicatedStore:
    """
    Simulates a distributed store. Large objects are split into chunks.
    Each chunk is replicated 3x across simulated storage nodes.
    """
    def __init__(self, chunk_size: int = 1024, replication_factor: int = 3):
        self.chunk_size = chunk_size
        self.replication_factor = replication_factor
        
        # logical_key -> List of Chunk IDs
        self.metadata_index: Dict[str, List[str]] = {}
        
        # node_id -> { chunk_id -> data }
        self.storage_nodes: Dict[int, Dict[str, bytes]] = {
            i: {} for i in range(5) # 5 simulated nodes
        }
        
        # chunk_id -> [node_id1, node_id2, node_id3]
        self.placement_map: Dict[str, List[int]] = {}

    def _hash(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def put(self, key: str, data: bytes):
        chunks = [data[i:i + self.chunk_size] for i in range(0, len(data), self.chunk_size)]
        chunk_ids = []
        
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{key}_part{idx}_{self._hash(chunk)[:8]}"
            chunk_ids.append(chunk_id)
            
            # Simple round-robin placement for replication
            nodes_for_chunk = []
            for r in range(self.replication_factor):
                node_id = (idx + r) % len(self.storage_nodes)
                self.storage_nodes[node_id][chunk_id] = chunk
                nodes_for_chunk.append(node_id)
                
            self.placement_map[chunk_id] = nodes_for_chunk
            
        self.metadata_index[key] = chunk_ids

    def get(self, key: str) -> bytes:
        if key not in self.metadata_index:
            raise KeyError(f"Object {key} not found")
            
        chunk_ids = self.metadata_index[key]
        assembled_data = bytearray()
        
        for chunk_id in chunk_ids:
            # Try to read from the first available replica
            nodes = self.placement_map.get(chunk_id, [])
            chunk_data = None
            
            for node_id in nodes:
                if chunk_id in self.storage_nodes[node_id]:
                    chunk_data = self.storage_nodes[node_id][chunk_id]
                    break # Read success
                    
            if chunk_data is None:
                raise RuntimeError(f"Data loss! Chunk {chunk_id} not found on any node.")
                
            assembled_data.extend(chunk_data)
            
        return bytes(assembled_data)

    def simulate_node_failure(self, node_id: int):
        """Wipes a node to simulate hardware failure"""
        if node_id in self.storage_nodes:
            self.storage_nodes[node_id] = {}

