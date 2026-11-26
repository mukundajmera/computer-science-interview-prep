public class SystemRequirements {
    private final int throughputTps;
    private final double readWriteRatio; // e.g., 10.0 means 10 reads per 1 write
    private final int latencySlaMs;
    private final ConsistencyLevel consistencyLevel;

    public SystemRequirements(int throughputTps, double readWriteRatio, int latencySlaMs, ConsistencyLevel consistencyLevel) {
        this.throughputTps = throughputTps;
        this.readWriteRatio = readWriteRatio;
        this.latencySlaMs = latencySlaMs;
        this.consistencyLevel = consistencyLevel;
    }

    public int getThroughputTps() {
        return throughputTps;
    }

    public double getReadWriteRatio() {
        return readWriteRatio;
    }

    public int getLatencySlaMs() {
        return latencySlaMs;
    }

    public ConsistencyLevel getConsistencyLevel() {
        return consistencyLevel;
    }
}
