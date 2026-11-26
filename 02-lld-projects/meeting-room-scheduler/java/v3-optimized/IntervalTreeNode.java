public class IntervalTreeNode {
    private Meeting meeting;
    private Interval interval;
    private long maxEnd;
    private IntervalTreeNode left;
    private IntervalTreeNode right;

    public IntervalTreeNode(Meeting meeting) {
        this.meeting = meeting;
        this.interval = meeting.getInterval();
        this.maxEnd = meeting.getInterval().getEndTime();
    }

    public Meeting getMeeting() {
        return meeting;
    }

    public Interval getInterval() {
        return interval;
    }

    public long getMaxEnd() {
        return maxEnd;
    }

    public void setMaxEnd(long maxEnd) {
        this.maxEnd = maxEnd;
    }

    public IntervalTreeNode getLeft() {
        return left;
    }

    public void setLeft(IntervalTreeNode left) {
        this.left = left;
    }

    public IntervalTreeNode getRight() {
        return right;
    }

    public void setRight(IntervalTreeNode right) {
        this.right = right;
    }
}
