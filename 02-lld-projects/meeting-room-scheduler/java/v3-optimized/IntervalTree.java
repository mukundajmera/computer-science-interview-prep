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

    public void remove(Meeting meeting) {
        root = remove(root, meeting);
    }

    private IntervalTreeNode remove(IntervalTreeNode node, Meeting meeting) {
        if (node == null) {
            return null;
        }

        if (meeting.getInterval().getStartTime() < node.getInterval().getStartTime()) {
            node.setLeft(remove(node.getLeft(), meeting));
        } else if (meeting.getInterval().getStartTime() > node.getInterval().getStartTime()) {
            node.setRight(remove(node.getRight(), meeting));
        } else {
            if (node.getMeeting().getId().equals(meeting.getId())) {
                if (node.getLeft() == null) {
                    return node.getRight();
                } else if (node.getRight() == null) {
                    return node.getLeft();
                }

                IntervalTreeNode minNode = getMinValueNode(node.getRight());
                // In java we can't easily mutate final fields if we used them, but let's assume we can swap or recreate
                // Wait, IntervalTreeNode fields are final for meeting and interval?
                // Let's check IntervalTreeNode.java
                // We'll have to change them to non-final or we can just swap left/right/maxEnd by replacing the node entirely.
                // It's easier to just recreate the node with minNode's values, but keeping the current left/right
                // Since we need to update the node itself, let's just make meeting/interval non-final in IntervalTreeNode.
                // Let's just create a new node and link it up.
                IntervalTreeNode newNode = new IntervalTreeNode(minNode.getMeeting());
                newNode.setLeft(node.getLeft());
                newNode.setRight(remove(node.getRight(), minNode.getMeeting()));
                node = newNode;
            } else {
                node.setRight(remove(node.getRight(), meeting));
            }
        }

        if (node != null) {
            updateMax(node);
        }

        return node;
    }
    
    private IntervalTreeNode getMinValueNode(IntervalTreeNode node) {
        IntervalTreeNode current = node;
        while (current.getLeft() != null) {
            current = current.getLeft();
        }
        return current;
    }
    
    private void updateMax(IntervalTreeNode node) {
        node.setMaxEnd(node.getInterval().getEndTime());
        if (node.getLeft() != null && node.getLeft().getMaxEnd() > node.getMaxEnd()) {
            node.setMaxEnd(node.getLeft().getMaxEnd());
        }
        if (node.getRight() != null && node.getRight().getMaxEnd() > node.getMaxEnd()) {
            node.setMaxEnd(node.getRight().getMaxEnd());
        }
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
