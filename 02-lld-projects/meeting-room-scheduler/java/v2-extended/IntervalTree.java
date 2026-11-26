import java.util.ArrayList;
import java.util.List;

public class IntervalTree {
    private IntervalTreeNode root;

    public void insert(Meeting meeting) {
        root = insert(root, meeting);
    }

    private IntervalTreeNode insert(IntervalTreeNode node, Meeting meeting) {
        if (node == null) {
            return new IntervalTreeNode(meeting);
        }

        if (meeting.getInterval().getStartTime() < node.getInterval().getStartTime()) {
            node.setLeft(insert(node.getLeft(), meeting));
        } else {
            node.setRight(insert(node.getRight(), meeting));
        }

        if (node.getMaxEnd() < meeting.getInterval().getEndTime()) {
            node.setMaxEnd(meeting.getInterval().getEndTime());
        }

        if (node.getLeft() != null && node.getLeft().getMaxEnd() > node.getMaxEnd()) {
            node.setMaxEnd(node.getLeft().getMaxEnd());
        }
        if (node.getRight() != null && node.getRight().getMaxEnd() > node.getMaxEnd()) {
            node.setMaxEnd(node.getRight().getMaxEnd());
        }

        return node;
    }

    public boolean hasOverlap(Interval interval) {
        return hasOverlap(root, interval);
    }

    private boolean hasOverlap(IntervalTreeNode node, Interval interval) {
        if (node == null) {
            return false;
        }

        if (node.getInterval().overlaps(interval)) {
            return true;
        }

        if (node.getLeft() != null && node.getLeft().getMaxEnd() > interval.getStartTime()) {
            if (hasOverlap(node.getLeft(), interval)) {
                return true;
            }
        }

        return hasOverlap(node.getRight(), interval);
    }

    public List<Meeting> getAllMeetings() {
        List<Meeting> meetings = new ArrayList<>();
        inOrder(root, meetings);
        return meetings;
    }

    private void inOrder(IntervalTreeNode node, List<Meeting> meetings) {
        if (node != null) {
            inOrder(node.getLeft(), meetings);
            meetings.add(node.getMeeting());
            inOrder(node.getRight(), meetings);
        }
    }
}
