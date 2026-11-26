"""EventDeduplicator for ad-click-aggregator (v2-extended)."""

class EventDeduplicator:
    def __init__(self, size: int = 1000000) -> None:
        self.bitset = bytearray((size + 7) // 8)
        self.size = size
        self.exact_store = set()

    def _hash(self, event_id: str) -> int:
        return hash(event_id) % self.size

    def is_duplicate(self, event_id: str) -> bool:
        idx = self._hash(event_id)
        byte_idx = idx // 8
        bit_idx = idx % 8
        
        # Probabilistic check
        if (self.bitset[byte_idx] & (1 << bit_idx)) != 0:
            # Exact check
            if event_id in self.exact_store:
                return True
        
        self.bitset[byte_idx] |= (1 << bit_idx)
        self.exact_store.add(event_id)
        return False
