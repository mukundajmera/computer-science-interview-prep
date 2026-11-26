public class IdComponents {
    public final long timestamp;
    public final long datacenterId;
    public final long workerId;
    public final long sequence;

    public IdComponents(long timestamp, long datacenterId, long workerId, long sequence) {
        this.timestamp = timestamp;
        this.datacenterId = datacenterId;
        this.workerId = workerId;
        this.sequence = sequence;
    }

    @Override
    public String toString() {
        return "IdComponents{" +
                "timestamp=" + timestamp +
                ", datacenterId=" + datacenterId +
                ", workerId=" + workerId +
                ", sequence=" + sequence +
                '}';
    }
}
