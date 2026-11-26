import os
import time
from typing import List

class LSMStore:
    def __init__(self, directory: str, threshold: int):
        self.directory = directory
        self.threshold = threshold
        self.mem_table = {}
        self.ss_tables: List[str] = []
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.wal_path = os.path.join(directory, "wal.log")
        self._load_sstables()
        self._recover()

    def _load_sstables(self):
        files = [f for f in os.listdir(self.directory) if f.endswith(".sst")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(self.directory, x)), reverse=True)
        self.ss_tables = [os.path.join(self.directory, f) for f in files]

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
        self.ss_tables.insert(0, sst_path)
        self.mem_table = {}
        if os.path.exists(self.wal_path):
            os.remove(self.wal_path)

    def get(self, key: str) -> str:
        val = self.mem_table.get(key)
        if val is not None:
            return None if val == "<TOMBSTONE>" else val

        for sst in self.ss_tables:
            with open(sst, "r") as f:
                for line in f:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2 and parts[0] == key:
                        return None if parts[1] == "<TOMBSTONE>" else parts[1]
        return None
