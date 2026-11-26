import os
import time
from typing import List

class LSMStore:
    def __init__(self, directory: str, threshold: int):
        self.directory = directory
        self.threshold = threshold
        self.mem_table = {}
        self.ss_tables: List[str] = []
        self.flush_crash_point = None
        self.append_crash_point = None
        self.bloom_filters = {}
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.wal_path = os.path.join(directory, "wal.log")
        self._load_sstables()
        self._recover()

    def _get_bloom_hash(self, key: str) -> int:
        return sum(ord(c) for c in key) % 64

    def _update_bloom_filter(self, sst_path: str):
        filter_val = 0
        with open(sst_path, "r") as f:
            for line in f:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    filter_val |= (1 << self._get_bloom_hash(parts[0]))
        self.bloom_filters[sst_path] = filter_val

    def _load_sstables(self):
        files = [f for f in os.listdir(self.directory) if f.endswith(".sst")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.directory, x)), reverse=True)
        self.ss_tables = [os.path.join(self.directory, f) for f in files]
        for sst in self.ss_tables:
            self._update_bloom_filter(sst)

    def _recover(self):
        if not os.path.exists(self.wal_path):
            return
        with open(self.wal_path, "r") as f:
            for line in f:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    self.mem_table[parts[0]] = parts[1]
        self._check_flush()

    def put(self, key: str, value: str):
        if self.append_crash_point is not None:
            self.append_crash_point()
        with open(self.wal_path, "a") as f:
            f.write(f"{key}={value}\n")
        self.mem_table[key] = value
        self._check_flush()

    def delete(self, key: str):
        self.put(key, "<TOMBSTONE>")

    def _check_flush(self):
        if len(self.mem_table) >= self.threshold:
            self._flush()

    def _flush(self):
        if not self.mem_table:
            return
        sst_path = os.path.join(self.directory, f"{time.time_ns()}.sst")
        with open(sst_path, "w") as f:
            for k, v in sorted(self.mem_table.items()):
                f.write(f"{k}={v}\n")
        if self.flush_crash_point is not None:
            self.flush_crash_point()
        self._update_bloom_filter(sst_path)
        self.ss_tables.insert(0, sst_path)
        self.mem_table = {}
        if os.path.exists(self.wal_path):
            os.remove(self.wal_path)

        if len(self.ss_tables) > 2:
            self._compact()

    def _compact(self):
        merged = {}
        for sst in reversed(self.ss_tables):
            with open(sst, "r") as f:
                for line in f:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        merged[parts[0]] = parts[1]

        compacted_path = os.path.join(self.directory, f"{time.time_ns()}_compacted.sst")
        with open(compacted_path, "w") as f:
            for k, v in sorted(merged.items()):
                f.write(f"{k}={v}\n")

        for sst in self.ss_tables:
            os.remove(sst)
            self.bloom_filters.pop(sst, None)
        self._update_bloom_filter(compacted_path)
        self.ss_tables = [compacted_path]

    def get(self, key: str) -> str:
        val = self.mem_table.get(key)
        if val is not None:
            return None if val == "<TOMBSTONE>" else val

        for sst in self.ss_tables:
            filter_val = self.bloom_filters.get(sst)
            if filter_val is not None and (filter_val & (1 << self._get_bloom_hash(key))) == 0:
                continue
            with open(sst, "r") as f:
                for line in f:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2 and parts[0] == key:
                        return None if parts[1] == "<TOMBSTONE>" else parts[1]
        return None
