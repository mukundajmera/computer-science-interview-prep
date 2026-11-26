import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.ConcurrentHashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.function.Function;

public class LiveReshardingMigrator {

    public enum MigrationPhase {
        PRE_MIGRATION,
        PHASE_1_DUAL_WRITE,
        PHASE_2_BACKFILL,
        PHASE_3_CDC,
        PHASE_4_SHADOW_READ,
        PHASE_5_CUTOVER,
        PHASE_6_DECOMMISSION
    }

    private MigrationPhase currentPhase = MigrationPhase.PRE_MIGRATION;
    
    // Simulate Data Stores
    private final Map<String, Record> sourceCluster = new ConcurrentHashMap<>();
    private final Map<String, Record> targetCluster = new ConcurrentHashMap<>();
    
    // Statistics for verification
    private int shadowReadDiscrepancies = 0;
    private int targetWriteFailures = 0;
    private int sourceWriteFailures = 0;

    public static class Record {
        public final String id;
        public final String data;
        public final long updatedAt;

        public Record(String id, String data, long updatedAt) {
            this.id = id;
            this.data = data;
            this.updatedAt = updatedAt;
        }
    }

    public void setPhase(MigrationPhase phase) {
        this.currentPhase = phase;
    }
    
    public MigrationPhase getPhase() {
        return this.currentPhase;
    }

    public void writeRecord(String id, String data, long timestamp) {
        Record record = new Record(id, data, timestamp);
        
        // Simulate explicit shard routing. 2 shards in source, 4 shards in target
        int sourceShard = Math.abs(id.hashCode()) % 2;
        int targetShard = Math.abs(id.hashCode()) % 4;
        
        String routedSourceId = "shard" + sourceShard + "_" + id;
        String routedTargetId = "shard" + targetShard + "_" + id;

        switch (currentPhase) {
            case PRE_MIGRATION:
                sourceCluster.put(routedSourceId, record);
                break;
            case PHASE_1_DUAL_WRITE:
            case PHASE_2_BACKFILL:
            case PHASE_3_CDC:
            case PHASE_4_SHADOW_READ:
                // Authoritative write to source
                sourceCluster.put(routedSourceId, record);
                // Best-effort write to target
                try {
                    targetCluster.put(routedTargetId, record);
                } catch (Exception e) {
                    targetWriteFailures++;
                }
                break;
            case PHASE_5_CUTOVER:
                // Authoritative write to target
                targetCluster.put(routedTargetId, record);
                // Best-effort write to source (reverse dual-write)
                try {
                    sourceCluster.put(routedSourceId, record);
                } catch (Exception e) {
                    sourceWriteFailures++;
                }
                break;
            case PHASE_6_DECOMMISSION:
                // Only target exists
                targetCluster.put(routedTargetId, record);
                break;
        }
    }

    public Record readRecord(String id) {
        int sourceShard = Math.abs(id.hashCode()) % 2;
        int targetShard = Math.abs(id.hashCode()) % 4;
        String routedSourceId = "shard" + sourceShard + "_" + id;
        String routedTargetId = "shard" + targetShard + "_" + id;

        switch (currentPhase) {
            case PRE_MIGRATION:
            case PHASE_1_DUAL_WRITE:
            case PHASE_2_BACKFILL:
            case PHASE_3_CDC:
                return sourceCluster.get(routedSourceId);
            case PHASE_4_SHADOW_READ:
                Record sourceRec = sourceCluster.get(routedSourceId);
                Record targetRec = targetCluster.get(routedTargetId);
                
                // Shadow read comparison
                if (sourceRec == null && targetRec != null) shadowReadDiscrepancies++;
                else if (sourceRec != null && targetRec == null) shadowReadDiscrepancies++;
                else if (sourceRec != null && targetRec != null && !sourceRec.data.equals(targetRec.data)) {
                    shadowReadDiscrepancies++;
                }
                
                // Return authoritative source
                return sourceRec;
            case PHASE_5_CUTOVER:
            case PHASE_6_DECOMMISSION:
                return targetCluster.get(routedTargetId);
            default:
                return null;
        }
    }

    public void runBackfillChunk(List<String> keys) {
        if (currentPhase != MigrationPhase.PHASE_2_BACKFILL) {
            return;
        }
        
        for (String key : keys) {
            int sourceShard = Math.abs(key.hashCode()) % 2;
            int targetShard = Math.abs(key.hashCode()) % 4;
            String routedSourceId = "shard" + sourceShard + "_" + key;
            String routedTargetId = "shard" + targetShard + "_" + key;

            Record sourceRec = sourceCluster.get(routedSourceId);
            if (sourceRec != null) {
                Record targetRec = targetCluster.get(routedTargetId);
                // Last-Write-Wins (LWW) resolution based on updated_at
                if (targetRec == null || targetRec.updatedAt < sourceRec.updatedAt) {
                    targetCluster.put(routedTargetId, sourceRec);
                }
            }
        }
    }
    
    // Test helper methods
    public int getTargetClusterSize() {
        return targetCluster.size();
    }
    
    public int getShadowReadDiscrepancies() {
        return shadowReadDiscrepancies;
    }
    
    public Record getTargetRecord(String id) {
        int targetShard = Math.abs(id.hashCode()) % 4;
        String routedTargetId = "shard" + targetShard + "_" + id;
        return targetCluster.get(routedTargetId);
    }
    
    public Record getSourceRecord(String id) {
        int sourceShard = Math.abs(id.hashCode()) % 2;
        String routedSourceId = "shard" + sourceShard + "_" + id;
        return sourceCluster.get(routedSourceId);
    }
    
    public void simulateTargetFailureDuringDualWrite(String id, String data, long timestamp) {
        int sourceShard = Math.abs(id.hashCode()) % 2;
        String routedSourceId = "shard" + sourceShard + "_" + id;
        Record record = new Record(id, data, timestamp);
        sourceCluster.put(routedSourceId, record);
        targetWriteFailures++;
    }
}
