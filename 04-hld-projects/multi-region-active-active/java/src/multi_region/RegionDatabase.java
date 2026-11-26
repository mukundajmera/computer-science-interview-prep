package multi_region;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.Collections;

public class RegionDatabase {
    private String regionName;
    private Map<String, Record> store;
    private HybridLogicalClock clock;
    private Map<String, Queue<Record>> replicationQueues; // Target Region -> Queue
    private boolean isPartitioned;

    public RegionDatabase(String regionName, List<String> peerRegions) {
        this.regionName = regionName;
        this.store = new ConcurrentHashMap<>();
        this.clock = new HybridLogicalClock(System.currentTimeMillis(), 0);
        this.replicationQueues = new ConcurrentHashMap<>();
        for (String peer : peerRegions) {
            replicationQueues.put(peer, new ConcurrentLinkedQueue<>());
        }
        this.isPartitioned = false;
    }

    public void setPartitioned(boolean partitioned) {
        this.isPartitioned = partitioned;
    }

    public HybridLogicalClock write(String id, String data) {
        long currentPhysicalTime = System.currentTimeMillis();
        clock.tick(currentPhysicalTime);
        
        Record record = new Record(id, data, clock.cloneClock(), regionName, false);
        store.put(id, record);
        
        // Enqueue for replication
        for (Queue<Record> queue : replicationQueues.values()) {
            queue.add(record);
        }
        
        return clock.cloneClock();
    }

    public Record read(String id) {
        return store.get(id);
    }

    // Process incoming replication
    public void applyReplication(Record incomingRecord) {
        long currentPhysicalTime = System.currentTimeMillis();
        clock.update(incomingRecord.getHlc(), currentPhysicalTime);
        
        store.compute(incomingRecord.getId(), (id, existingRecord) -> {
            if (existingRecord == null) {
                return incomingRecord;
            }
            
            int comparison = incomingRecord.getHlc().compareTo(existingRecord.getHlc());
            if (comparison > 0) {
                return incomingRecord;
            } else if (comparison == 0) {
                // Tie breaker using region name
                if (incomingRecord.getOriginRegion().compareTo(existingRecord.getOriginRegion()) > 0) {
                    return incomingRecord;
                } else {
                    return existingRecord;
                }
            } else {
                return existingRecord; // Existing is newer
            }
        });
    }

    public void replicateTo(RegionDatabase targetDb) {
        if (this.isPartitioned || targetDb.isPartitioned) {
            return; // Network partition simulation
        }
        
        Queue<Record> queue = replicationQueues.get(targetDb.regionName);
        if (queue != null) {
            while (!queue.isEmpty()) {
                Record record = queue.poll();
                targetDb.applyReplication(record);
            }
        }
    }
}
