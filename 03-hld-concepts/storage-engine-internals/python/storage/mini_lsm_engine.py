import threading
from typing import Dict, Optional, List

TOMBSTONE = "<TOMBSTONE>"

class BloomFilter:
    def __init__(self, size: int, num_hashes: int):
        self.size = size
        self.num_hashes = num_hashes
        # Simple boolean list to simulate bitset
        self.bit_set = [False] * size

    def add(self, key: str):
        for i in range(self.num_hashes):
            h = self._get_hash(key, i)
            self.bit_set[h] = True

    def might_contain(self, key: str) -> bool:
        for i in range(self.num_hashes):
            h = self._get_hash(key, i)
            if not self.bit_set[h]:
                return False
        return True

    def _get_hash(self, key: str, i: int) -> int:
        h = hash(key) ^ (i * 0x5bd1e995)
        return abs(h) % self.size

class SSTable:
    BLOCK_SIZE = 2

    def __init__(self, data: Dict[str, str]):
        # Keep data sorted
        self.data = dict(sorted(data.items()))
        self.sparse_index = []
        self.bloom_filter = BloomFilter(100, 3)

        count = 0
        for key in self.data:
            if count % self.BLOCK_SIZE == 0:
                self.sparse_index.append(key)
            self.bloom_filter.add(key)
            count += 1

    def might_contain(self, key: str) -> bool:
        return self.bloom_filter.might_contain(key)

    def get(self, key: str) -> Optional[str]:
        if not self.sparse_index:
            return None
        return self.data.get(key)

class MiniLsmEngine:
    def __init__(self, mem_table_threshold: int):
        self.mem_table_threshold = mem_table_threshold
        self.mem_table: Dict[str, str] = {}
        self.current_mem_table_size = 0
        self.ss_tables: List[SSTable] = []
        self.lock = threading.Lock()

    def put(self, key: str, value: str):
        with self.lock:
            entry_size = len(key.encode('utf-8')) + len(value.encode('utf-8'))
            if self.current_mem_table_size + entry_size > self.mem_table_threshold:
                self._flush()
            self.mem_table[key] = value
            self.current_mem_table_size += entry_size

    def delete(self, key: str):
        self.put(key, TOMBSTONE)

    def get(self, key: str) -> Optional[str]:
        with self.lock:
            # Check mem_table first
            if key in self.mem_table:
                val = self.mem_table[key]
                return None if val == TOMBSTONE else val

            # Check SSTables from newest to oldest
            for table in reversed(self.ss_tables):
                if table.might_contain(key):
                    val = table.get(key)
                    if val is not None:
                        return None if val == TOMBSTONE else val
            
            return None

    def _flush(self):
        if not self.mem_table:
            return
        
        new_table = SSTable(self.mem_table)
        self.ss_tables.append(new_table)
        self.mem_table = {}
        self.current_mem_table_size = 0

    def compact(self):
        with self.lock:
            self._flush()
            if len(self.ss_tables) <= 1:
                return

            merged_data = {}
            for table in self.ss_tables:
                for k, v in table.data.items():
                    merged_data[k] = v

            # Remove tombstones
            merged_data = {k: v for k, v in merged_data.items() if v != TOMBSTONE}

            compacted_table = SSTable(merged_data)
            self.ss_tables.clear()
            self.ss_tables.append(compacted_table)

    def get_ss_tables_count(self) -> int:
        with self.lock:
            return len(self.ss_tables)
