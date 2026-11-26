import unittest
from src.live_resharding_migrator import LiveReshardingMigrator, MigrationPhase

class TestLiveReshardingMigrator(unittest.TestCase):

    def test_phase_1_dual_write(self):
        migrator = LiveReshardingMigrator()
        migrator.set_phase(MigrationPhase.PHASE_1_DUAL_WRITE)
        
        migrator.write_record("user1", "data_v1", 1000)
        
        self.assertIsNotNone(migrator.get_source_record("user1"))
        self.assertIsNotNone(migrator.get_target_record("user1"))
        self.assertEqual(migrator.get_source_record("user1").data, "data_v1")
        self.assertEqual(migrator.get_target_record("user1").data, "data_v1")

    def test_phase_2_backfill_lww(self):
        migrator = LiveReshardingMigrator()
        
        # 1. New write arrives via dual write
        migrator.set_phase(MigrationPhase.PHASE_1_DUAL_WRITE)
        migrator.write_record("user1", "new_data", 1000)
        
        # 2. Simulate backfill reading an old snapshot from source
        # We downgrade the source record to an older timestamp to mimic a stale snapshot being read
        migrator.set_phase(MigrationPhase.PRE_MIGRATION)
        migrator.write_record("user1", "old_snapshot_data", 500)
        
        # 3. Run backfill chunk
        migrator.set_phase(MigrationPhase.PHASE_2_BACKFILL)
        migrator.run_backfill_chunk(["user1"])
        
        # Target should retain the newer data (timestamp 1000) due to LWW
        target_record = migrator.get_target_record("user1")
        self.assertIsNotNone(target_record)
        self.assertEqual(target_record.data, "new_data")
        self.assertEqual(target_record.updated_at, 1000)

    def test_phase_4_shadow_reads_discrepancy(self):
        migrator = LiveReshardingMigrator()
        
        # Write only to source (simulating missed dual-write or pre-migration data)
        migrator.set_phase(MigrationPhase.PRE_MIGRATION)
        migrator.write_record("user1", "auth_data", 1000)
        
        # Switch to shadow read phase
        migrator.set_phase(MigrationPhase.PHASE_4_SHADOW_READ)
        result = migrator.read_record("user1")
        
        # Should return source data
        self.assertIsNotNone(result)
        self.assertEqual(result.data, "auth_data")
        
        # Should detect discrepancy because target is missing the record
        self.assertEqual(migrator.get_shadow_read_discrepancies(), 1)

    def test_phase_4_shadow_reads_clean(self):
        migrator = LiveReshardingMigrator()
        
        # Write cleanly to both
        migrator.set_phase(MigrationPhase.PHASE_1_DUAL_WRITE)
        migrator.write_record("user1", "clean_data", 1000)
        
        # Shadow read
        migrator.set_phase(MigrationPhase.PHASE_4_SHADOW_READ)
        result = migrator.read_record("user1")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.data, "clean_data")
        self.assertEqual(migrator.get_shadow_read_discrepancies(), 0)

    def test_phase_5_write_authority_inversion(self):
        migrator = LiveReshardingMigrator()
        
        # Phase 5: target is authoritative
        migrator.set_phase(MigrationPhase.PHASE_5_CUTOVER)
        migrator.write_record("user1", "target_auth_data", 1000)
        
        # Read should come from target
        result = migrator.read_record("user1")
        self.assertIsNotNone(result)
        self.assertEqual(result.data, "target_auth_data")
        
        # Reverse dual-write should populate source
        source_record = migrator.get_source_record("user1")
        self.assertIsNotNone(source_record)
        self.assertEqual(source_record.data, "target_auth_data")

if __name__ == '__main__':
    unittest.main()
