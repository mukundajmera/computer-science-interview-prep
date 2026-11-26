from typing import Dict, List, Tuple

class V3XorParityStore:
    """
    Simulates a simplified Erasure Coding (RAID-4 style K+1 Parity using XOR).
    Real RS EC uses Galois Field polynomial arithmetic, but XOR demonstrates
    the degraded read and repair mechanics mathematically.
    """
    def __init__(self, data_chunks_k: int = 4):
        self.k = data_chunks_k
        self.metadata_index: Dict[str, Dict] = {}
        # Simple node abstraction: node_index -> chunk_data
        self.nodes: Dict[int, Dict[str, bytes]] = {i: {} for i in range(self.k + 1)}

    def _xor_bytes(self, b1: bytes, b2: bytes) -> bytes:
        return bytes(x ^ y for x, y in zip(b1, b2))

    def put(self, key: str, data: bytes):
        # Pad data so it is divisible by K
        remainder = len(data) % self.k
        if remainder != 0:
            data += b'\x00' * (self.k - remainder)
            
        chunk_size = len(data) // self.k
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
        
        # Calculate XOR Parity chunk
        parity = chunks[0]
        for i in range(1, self.k):
            parity = self._xor_bytes(parity, chunks[i])
            
        chunks.append(parity) # K data chunks + 1 parity chunk
        
        # Store metadata
        self.metadata_index[key] = {
            'original_length': len(data) - (self.k - remainder) if remainder else len(data),
            'chunk_size': chunk_size,
            'chunk_ids': []
        }
        
        # Write to "nodes"
        for i, chunk in enumerate(chunks):
            chunk_id = f"{key}_c{i}"
            self.metadata_index[key]['chunk_ids'].append(chunk_id)
            self.nodes[i][chunk_id] = chunk

    def _read_chunk(self, node_id: int, chunk_id: str) -> bytes:
        if node_id not in self.nodes or chunk_id not in self.nodes[node_id]:
            return None
        return self.nodes[node_id][chunk_id]

    def get(self, key: str) -> bytes:
        if key not in self.metadata_index:
            raise KeyError("Not found")
            
        meta = self.metadata_index[key]
        assembled = bytearray()
        
        for i in range(self.k):
            chunk_id = meta['chunk_ids'][i]
            chunk = self._read_chunk(i, chunk_id)
            
            if chunk is None:
                # Degraded Read: Reconstruct missing data chunk using XOR
                # Missing Data = (All other Data) XOR Parity
                print(f"Node {i} offline. Performing degraded read for {chunk_id}")
                reconstructed = bytearray(meta['chunk_size'])
                
                # XOR all available surviving chunks (data + parity)
                for j in range(self.k + 1):
                    if i == j: continue # Skip the missing one
                    surviving_chunk = self._read_chunk(j, meta['chunk_ids'][j])
                    if surviving_chunk is None:
                        raise RuntimeError(f"Multiple failures! Cannot reconstruct {key}")
                    reconstructed = self._xor_bytes(reconstructed, surviving_chunk)
                chunk = bytes(reconstructed)
                
            assembled.extend(chunk)
            
        # Strip padding
        return bytes(assembled[:meta['original_length']])

    def scrub_and_repair(self, key: str):
        """Background job to fix a missing chunk permanently"""
        if key not in self.metadata_index:
            return
            
        meta = self.metadata_index[key]
        missing_idx = -1
        
        # Find missing chunk
        for i in range(self.k + 1):
            chunk_id = meta['chunk_ids'][i]
            if self._read_chunk(i, chunk_id) is None:
                missing_idx = i
                break
                
        if missing_idx != -1:
            # Reconstruct and rewrite
            reconstructed = bytearray(meta['chunk_size'])
            for j in range(self.k + 1):
                if missing_idx == j: continue
                surviving_chunk = self._read_chunk(j, meta['chunk_ids'][j])
                reconstructed = self._xor_bytes(reconstructed, surviving_chunk)
                
            # Repair
            self.nodes[missing_idx][meta['chunk_ids'][missing_idx]] = bytes(reconstructed)
            return True
        return False

    def simulate_node_failure(self, node_id: int):
        self.nodes[node_id] = {}

