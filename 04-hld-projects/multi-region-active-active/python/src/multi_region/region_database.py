import time
import threading
from typing import Dict, List
import queue
from .hybrid_logical_clock import HybridLogicalClock
from .record import Record

def current_time_ms() -> int:
    return int(time.time() * 1000)

class RegionDatabase:
    def __init__(self, region_name: str, peer_regions: List[str]):
        self.region_name = region_name
        self.store: Dict[str, Record] = {}
        self.clock = HybridLogicalClock(current_time_ms(), 0)
        self.replication_queues: Dict[str, queue.Queue] = {peer: queue.Queue() for peer in peer_regions}
        self.is_partitioned = False
        self._lock = threading.Lock()

    def set_partitioned(self, partitioned: bool):
        self.is_partitioned = partitioned

    def write(self, record_id: str, data: str) -> HybridLogicalClock:
        self.clock.tick(current_time_ms())
        record = Record(record_id, data, self.clock.clone_clock(), self.region_name)
        
        with self._lock:
            self.store[record_id] = record
            
            for q in self.replication_queues.values():
                q.put(record)
                
        return self.clock.clone_clock()

    def read(self, record_id: str) -> Record:
        with self._lock:
            return self.store.get(record_id)

    def apply_replication(self, incoming_record: Record):
        self.clock.update(incoming_record.hlc, current_time_ms())
        
        with self._lock:
            existing_record = self.store.get(incoming_record.id)
            if existing_record is None:
                self.store[incoming_record.id] = incoming_record
                return

            if incoming_record.hlc > existing_record.hlc:
                self.store[incoming_record.id] = incoming_record
            elif incoming_record.hlc == existing_record.hlc:
                if incoming_record.origin_region > existing_record.origin_region:
                    self.store[incoming_record.id] = incoming_record

    def replicate_to(self, target_db: 'RegionDatabase'):
        if self.is_partitioned or target_db.is_partitioned:
            return
            
        target_queue = self.replication_queues.get(target_db.region_name)
        if target_queue:
            while not target_queue.empty():
                try:
                    record = target_queue.get_nowait()
                    target_db.apply_replication(record)
                except queue.Empty:
                    break
