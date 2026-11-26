import os
import time

class LSMStore:
    def __init__(self, directory: str, threshold: int = 100):
        self.directory = directory
        self.mem_table = {}
        self.threshold = threshold
        if not os.path.exists(directory):
            os.makedirs(directory)
        self.wal_path = os.path.join(directory, "wal.log")
        self.ss_tables = []
        self.flush_crash_point = None
        self.wal_crash_point = None
        self._load_sstables()
        self._recover()

    def _load_sstables(self):
        if not os.path.exists(self.directory):
            return
        files = [f for f in os.listdir(self.directory) if f.endswith('.sst')]
        full_paths = [os.path.join(self.directory, f) for f in files]
        full_paths.sort(key=os.path.getmtime, reverse=True)
        self.ss_tables.extend(full_paths)

    def _recover(self):
        if not os.path.exists(self.wal_path):
            return
        with open(self.wal_path, "r") as f:
            for line in f:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    if parts[1] == "<TOMBSTONE>":
                        self.mem_table[parts[0]] = "<TOMBSTONE>"
                    else:
                        self.mem_table[parts[0]] = parts[1]
        self._check_flush()

    def put(self, key: str, value: str):
        if self.wal_crash_point:
            self.wal_crash_point()
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
        timestamp = int(time.time() * 1000)
        sst_file = os.path.join(self.directory, f"{timestamp}.sst")
        with open(sst_file, "w") as f:
            for k, v in sorted(self.mem_table.items()):
                f.write(f"{k}={v}\n")
            if self.flush_crash_point:
                self.flush_crash_point()
        
        self.ss_tables.insert(0, sst_file)
        self.mem_table.clear()
        if os.path.exists(self.wal_path):
            os.remove(self.wal_path)

    def get(self, key: str) -> str:
        if key in self.mem_table:
            val = self.mem_table[key]
            return None if val == "<TOMBSTONE>" else val
        
        for sst in self.ss_tables:
            if not os.path.exists(sst):
                continue
            with open(sst, "r") as f:
                for line in f:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2 and parts[0] == key:
                        return None if parts[1] == "<TOMBSTONE>" else parts[1]
        return None
