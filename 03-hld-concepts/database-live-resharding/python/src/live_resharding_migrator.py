from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass

class MigrationPhase(Enum):
    PRE_MIGRATION = 0
    PHASE_1_DUAL_WRITE = 1
    PHASE_2_BACKFILL = 2
    PHASE_3_CDC = 3
    PHASE_4_SHADOW_READ = 4
    PHASE_5_CUTOVER = 5
    PHASE_6_DECOMMISSION = 6

@dataclass
class Record:
    id: str
    data: str
    updated_at: int

class LiveReshardingMigrator:
    def __init__(self):
        self.current_phase = MigrationPhase.PRE_MIGRATION
        self.source_cluster: Dict[str, Record] = {}
        self.target_cluster: Dict[str, Record] = {}
        
        self.shadow_read_discrepancies = 0
        self.target_write_failures = 0
        self.source_write_failures = 0

    def set_phase(self, phase: MigrationPhase):
        self.current_phase = phase

    def get_phase(self) -> MigrationPhase:
        return self.current_phase

    def write_record(self, record_id: str, data: str, timestamp: int):
        record = Record(id=record_id, data=data, updated_at=timestamp)

        # Simulate explicit shard routing. 2 shards in source, 4 shards in target
        source_shard = str(hash(record_id) % 2)
        target_shard = str(hash(record_id) % 4)
        
        # we prefix the ID with the shard routing to ensure this logic runs, but store it flatly
        routed_source_id = f"shard{source_shard}_{record_id}"
        routed_target_id = f"shard{target_shard}_{record_id}"

        if self.current_phase == MigrationPhase.PRE_MIGRATION:
            self.source_cluster[routed_source_id] = record
            
        elif self.current_phase in (MigrationPhase.PHASE_1_DUAL_WRITE, MigrationPhase.PHASE_2_BACKFILL,
                                  MigrationPhase.PHASE_3_CDC, MigrationPhase.PHASE_4_SHADOW_READ):
            # Authoritative write to source
            self.source_cluster[routed_source_id] = record
            # Best-effort write to target
            try:
                self.target_cluster[routed_target_id] = record
            except Exception:
                self.target_write_failures += 1
                
        elif self.current_phase == MigrationPhase.PHASE_5_CUTOVER:
            # Authoritative write to target
            self.target_cluster[routed_target_id] = record
            # Best-effort write to source
            try:
                self.source_cluster[routed_source_id] = record
            except Exception:
                self.source_write_failures += 1
                
        elif self.current_phase == MigrationPhase.PHASE_6_DECOMMISSION:
            self.target_cluster[routed_target_id] = record

    def read_record(self, record_id: str) -> Optional[Record]:
        source_shard = str(hash(record_id) % 2)
        target_shard = str(hash(record_id) % 4)
        routed_source_id = f"shard{source_shard}_{record_id}"
        routed_target_id = f"shard{target_shard}_{record_id}"
        
        if self.current_phase in (MigrationPhase.PRE_MIGRATION, MigrationPhase.PHASE_1_DUAL_WRITE,
                                MigrationPhase.PHASE_2_BACKFILL, MigrationPhase.PHASE_3_CDC):
            return self.source_cluster.get(routed_source_id)
            
        elif self.current_phase == MigrationPhase.PHASE_4_SHADOW_READ:
            source_rec = self.source_cluster.get(routed_source_id)
            target_rec = self.target_cluster.get(routed_target_id)
            
            # Shadow read comparison
            if source_rec is None and target_rec is not None:
                self.shadow_read_discrepancies += 1
            elif source_rec is not None and target_rec is None:
                self.shadow_read_discrepancies += 1
            elif source_rec is not None and target_rec is not None and source_rec.data != target_rec.data:
                self.shadow_read_discrepancies += 1
                
            return source_rec
            
        elif self.current_phase in (MigrationPhase.PHASE_5_CUTOVER, MigrationPhase.PHASE_6_DECOMMISSION):
            return self.target_cluster.get(routed_target_id)
            
        return None

    def run_backfill_chunk(self, keys: List[str]):
        if self.current_phase != MigrationPhase.PHASE_2_BACKFILL:
            return
            
        for key in keys:
            source_shard = str(hash(key) % 2)
            target_shard = str(hash(key) % 4)
            routed_source_id = f"shard{source_shard}_{key}"
            routed_target_id = f"shard{target_shard}_{key}"

            source_rec = self.source_cluster.get(routed_source_id)
            if source_rec:
                target_rec = self.target_cluster.get(routed_target_id)
                # Last-Write-Wins (LWW) resolution based on updated_at
                if not target_rec or target_rec.updated_at < source_rec.updated_at:
                    self.target_cluster[routed_target_id] = source_rec

    # Test helpers
    def get_target_cluster_size(self) -> int:
        return len(self.target_cluster)
        
    def get_shadow_read_discrepancies(self) -> int:
        return self.shadow_read_discrepancies
        
    def get_target_record(self, record_id: str) -> Optional[Record]:
        target_shard = str(hash(record_id) % 4)
        routed_target_id = f"shard{target_shard}_{record_id}"
        return self.target_cluster.get(routed_target_id)
        
    def get_source_record(self, record_id: str) -> Optional[Record]:
        source_shard = str(hash(record_id) % 2)
        routed_source_id = f"shard{source_shard}_{record_id}"
        return self.source_cluster.get(routed_source_id)

    def simulate_target_failure_during_dual_write(self, record_id: str, data: str, timestamp: int):
        source_shard = str(hash(record_id) % 2)
        routed_source_id = f"shard{source_shard}_{record_id}"
        record = Record(id=record_id, data=data, updated_at=timestamp)
        self.source_cluster[routed_source_id] = record
        self.target_write_failures += 1
