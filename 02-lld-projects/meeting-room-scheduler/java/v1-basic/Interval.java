public class Interval {
    private final long startTime;
    private final long endTime;

    public Interval(long startTime, long endTime) {
        if (startTime >= endTime) {
            throw new IllegalArgumentException("Start time must be before end time");
        }
        this.startTime = startTime;
        this.endTime = endTime;
    }

    public long getStartTime() {
        return startTime;
    }

    public long getEndTime() {
        return endTime;
    }

    public boolean overlaps(Interval other) {
        return this.startTime < other.getEndTime() && other.getStartTime() < this.endTime;
    }

    @Override
    public String toString() {
        return "[" + startTime + ", " + endTime + ")";
    }
}
