package v1_basic.multi_region;

public class HybridLogicalClock {
    private long physicalTime;
    private int logicalCounter;

    public HybridLogicalClock(long physicalTime, int logicalCounter) {
        this.physicalTime = physicalTime;
        this.logicalCounter = logicalCounter;
    }

    public synchronized void tick(long currentPhysicalTime) {
        if (currentPhysicalTime > physicalTime) {
            physicalTime = currentPhysicalTime;
            logicalCounter = 0;
        } else {
            logicalCounter++;
        }
    }

    public synchronized void update(HybridLogicalClock other, long currentPhysicalTime) {
        if (currentPhysicalTime > physicalTime && currentPhysicalTime > other.physicalTime) {
            physicalTime = currentPhysicalTime;
            logicalCounter = 0;
        } else if (physicalTime == other.physicalTime) {
            logicalCounter = Math.max(logicalCounter, other.logicalCounter) + 1;
        } else if (physicalTime > other.physicalTime) {
            logicalCounter++;
        } else {
            physicalTime = other.physicalTime;
            logicalCounter = other.logicalCounter + 1;
        }
    }

    public long getPhysicalTime() {
        return physicalTime;
    }

    public int getLogicalCounter() {
        return logicalCounter;
    }
    
    public synchronized HybridLogicalClock cloneClock() {
        return new HybridLogicalClock(this.physicalTime, this.logicalCounter);
    }

    public int compareTo(HybridLogicalClock other) {
        if (this.physicalTime == other.physicalTime) {
            return Integer.compare(this.logicalCounter, other.logicalCounter);
        }
        return Long.compare(this.physicalTime, other.physicalTime);
    }
}
