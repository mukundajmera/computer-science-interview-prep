import os
import json
import hashlib
from typing import List, Optional, Tuple, Dict

class BloomFilter:
    def __init__(self, size: int = 1000, hash_count: int = 3):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [False] * size

    def _hashes(self, item: str) -> List[int]:
        hashes = []
        for i in range(self.hash_count):
            h = int(hashlib.sha256((item + str(i)).encode('utf-8')).hexdigest(), 16)
            hashes.append(h % self.size)
        return hashes

    def add(self, item: str):
        for h in self._hashes(item):
            self.bit_array[h] = True

    def might_contain(self, item: str) -> bool:
        for h in self._hashes(item):
            if not self.bit_array[h]:
                return False
        return True

class SSTable:
    def __init__(self, filename: str, data: List[Tuple[str, Optional[str]]]):
        self.filename = filename
        self.bloom_filter = BloomFilter(size=max(100, len(data) * 10), hash_count=3)
        self.index: Dict[str, int] = {}
        self.data = data

        for idx, (k, v) in enumerate(data):
            self.bloom_filter.add(k)
            self.index[k] = idx

        self._write_to_disk()

    def _write_to_disk(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

    def read_from_disk(self) -> List[Tuple[str, Optional[str]]]:
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, 'r') as f:
            return json.load(f)

    def get(self, key: str) -> Tuple[bool, Optional[str]]:
        if not self.bloom_filter.might_contain(key):
            return False, None

        if key in self.index:
            idx = self.index[key]
            data = self.read_from_disk()
            if idx < len(data) and data[idx][0] == key:
                return True, data[idx][1]

        return False, None

    def scan(self, start_key: str, end_key: str) -> List[Tuple[str, Optional[str]]]:
        data = self.read_from_disk()
        result = []
        for k, v in data:
            if start_key <= k <= end_key:
                result.append((k, v))
        return result

class LsmKeyStore:
    def __init__(self, memtable_threshold: int = 5, data_dir: str = "lsm_data"):
        self.memtable_threshold = memtable_threshold
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

        self.memtable: Dict[str, Optional[str]] = {}
        self.wal: List[Tuple[str, Optional[str]]] = []
        self.wal_filename = os.path.join(self.data_dir, "wal.log")
        self.sstables: List[SSTable] = []
        self.sstable_counter = 0

        self._recover()

    def _recover(self):
        if os.path.exists(self.wal_filename):
            with open(self.wal_filename, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    parts = json.loads(line.strip())
                    k, v = parts[0], parts[1]
                    self.memtable[k] = v
                    self.wal.append((k, v))

            if len(self.memtable) >= self.memtable_threshold:
                self._flush_memtable()

    def _append_wal(self, key: str, value: Optional[str]):
        self.wal.append((key, value))
        with open(self.wal_filename, 'a') as f:
            f.write(json.dumps([key, value]) + '\n')

    def _flush_memtable(self):
        if not self.memtable:
            return

        sorted_items = sorted(self.memtable.items())
        filename = os.path.join(self.data_dir, f"sstable_{self.sstable_counter}.json")
        self.sstable_counter += 1

        sstable = SSTable(filename, sorted_items)
        self.sstables.insert(0, sstable)

        self.memtable = {}
        self.wal = []
        if os.path.exists(self.wal_filename):
            os.remove(self.wal_filename)

    def put(self, key: str, value: str):
        self._append_wal(key, value)
        self.memtable[key] = value
        if len(self.memtable) >= self.memtable_threshold:
            self._flush_memtable()

    def delete(self, key: str):
        self._append_wal(key, None)
        self.memtable[key] = None
        if len(self.memtable) >= self.memtable_threshold:
            self._flush_memtable()

    def get(self, key: str) -> Optional[str]:
        if key in self.memtable:
            return self.memtable[key]

        for sstable in self.sstables:
            found, value = sstable.get(key)
            if found:
                return value

        return None

    def scan(self, start_key: str, end_key: str) -> List[Tuple[str, str]]:
        merged: Dict[str, Optional[str]] = {}

        for sstable in reversed(self.sstables):
            for k, v in sstable.scan(start_key, end_key):
                merged[k] = v

        for k, v in self.memtable.items():
            if start_key <= k <= end_key:
                merged[k] = v

        result = []
        for k in sorted(merged.keys()):
            v = merged[k]
            if v is not None:
                result.append((k, v))

        return result
