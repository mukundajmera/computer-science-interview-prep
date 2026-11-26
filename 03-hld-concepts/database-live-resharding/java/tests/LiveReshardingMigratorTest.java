import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;

public class LiveReshardingMigratorTest {

    private LiveReshardingMigrator migrator;

    @BeforeEach
    public void setup() {
        migrator = new LiveReshardingMigrator();
    }

    @Test
    public void testPhase1DualWrite() {
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_1_DUAL_WRITE);
        migrator.writeRecord("user1", "data_v1", 1000L);

        // Record should exist in both clusters
        assertNotNull(migrator.getSourceRecord("user1"));
        assertNotNull(migrator.getTargetRecord("user1"));
        assertEquals("data_v1", migrator.getSourceRecord("user1").data);
        assertEquals("data_v1", migrator.getTargetRecord("user1").data);
    }

    @Test
    public void testLWWBackfillProperly() {
        // Since we can't easily mock the internal state, let's just test the logic
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_2_BACKFILL);
        
        // Write to source and target
        migrator.writeRecord("key1", "target_newer", 500L);
        
        // Manually simulate target having a newer record (e.g. from a recent dual-write)
        // and source having an older record (e.g. from the backfill snapshot)
        // We can't do this easily with the current API unless we simulate target failure during dual write
        LiveReshardingMigrator migratorLww = new LiveReshardingMigrator() {
            @Override
            public void runBackfillChunk(java.util.List<String> keys) {
                super.runBackfillChunk(keys);
            }
        };
        migratorLww.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_2_BACKFILL);
        
        // Suppose target has a record with timestamp 1000
        migratorLww.writeRecord("key1", "new_data", 1000L);
        
        // We can simulate a stale backfill by changing phase to PRE_MIGRATION and writing an old value to source
        migratorLww.setPhase(LiveReshardingMigrator.MigrationPhase.PRE_MIGRATION);
        migratorLww.writeRecord("key1", "old_snapshot_data", 500L);
        
        // Now run backfill chunk
        migratorLww.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_2_BACKFILL);
        migratorLww.runBackfillChunk(Arrays.asList("key1"));
        
        // The target should still have the new data because of LWW (1000 > 500)
        assertEquals("new_data", migratorLww.getTargetRecord("key1").data);
        assertEquals(1000L, migratorLww.getTargetRecord("key1").updatedAt);
    }

    @Test
    public void testPhase4ShadowReadsDiscrepancy() {
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PRE_MIGRATION);
        migrator.writeRecord("user1", "auth_data", 1000L);
        
        // Missing in target
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_4_SHADOW_READ);
        LiveReshardingMigrator.Record result = migrator.readRecord("user1");
        
        assertEquals("auth_data", result.data); // Should return authoritative source data
        assertEquals(1, migrator.getShadowReadDiscrepancies()); // Should log discrepancy
        
        // Clean up from the code review notes
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PRE_MIGRATION);
        migrator.writeRecord("user2", "source_val", 2000L);
        // By bypassing normal cutover writes and simulating failure we achieve discrepancy
        migrator.simulateTargetFailureDuringDualWrite("user2", "target_val", 2000L); 
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_4_SHADOW_READ);
        migrator.readRecord("user2");
    }
    
    @Test
    public void testPhase4ShadowReadsClean() {
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_1_DUAL_WRITE);
        migrator.writeRecord("user1", "clean_data", 1000L);
        
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_4_SHADOW_READ);
        LiveReshardingMigrator.Record result = migrator.readRecord("user1");
        
        assertEquals("clean_data", result.data);
        assertEquals(0, migrator.getShadowReadDiscrepancies());
    }

    @Test
    public void testPhase5WriteAuthorityInversion() {
        migrator.setPhase(LiveReshardingMigrator.MigrationPhase.PHASE_5_CUTOVER);
        migrator.writeRecord("user1", "target_auth_data", 1000L);
        
        LiveReshardingMigrator.Record readResult = migrator.readRecord("user1");
        
        // Read should come from target cluster
        assertEquals("target_auth_data", readResult.data);
        assertNotNull(migrator.getSourceRecord("user1")); // Reverse dual-write ensures source gets it too
    }
}