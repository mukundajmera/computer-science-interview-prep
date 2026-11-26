from typing import Optional, List
from interval import Interval
from meeting import Meeting

class IntervalTreeNode:
    def __init__(self, meeting: Meeting):
        self.meeting = meeting
        self.interval = meeting.interval
        self.max_end = meeting.interval.end_time
        self.left: Optional['IntervalTreeNode'] = None
        self.right: Optional['IntervalTreeNode'] = None

class IntervalTree:
    def __init__(self):
        self.root: Optional[IntervalTreeNode] = None

    def insert(self, meeting: Meeting) -> None:
        self.root = self._insert(self.root, meeting)

    def _insert(self, root: Optional[IntervalTreeNode], meeting: Meeting) -> IntervalTreeNode:
        if root is None:
            return IntervalTreeNode(meeting)

        if meeting.interval.start_time < root.interval.start_time:
            root.left = self._insert(root.left, meeting)
        else:
            root.right = self._insert(root.right, meeting)

        if root.max_end < meeting.interval.end_time:
            root.max_end = meeting.interval.end_time
        
        if root.left and root.left.max_end > root.max_end:
            root.max_end = root.left.max_end
        if root.right and root.right.max_end > root.max_end:
            root.max_end = root.right.max_end

        return root

    def remove(self, meeting: Meeting) -> None:
        # Simplest way for balanced trees or simple BSTs is often just a rebuild or standard delete.
        # Here we'll do a standard BST delete by interval start time, then recompute max_end along path.
        self.root = self._remove(self.root, meeting)

    def _remove(self, root: Optional[IntervalTreeNode], meeting: Meeting) -> Optional[IntervalTreeNode]:
        if root is None:
            return None

        if meeting.interval.start_time < root.interval.start_time:
            root.left = self._remove(root.left, meeting)
        elif meeting.interval.start_time > root.interval.start_time:
            root.right = self._remove(root.right, meeting)
        else:
            if root.meeting.id == meeting.id:
                if root.left is None:
                    return root.right
                elif root.right is None:
                    return root.left
                
                # Node with two children: Get inorder successor (smallest in the right subtree)
                temp = self._min_value_node(root.right)
                root.meeting = temp.meeting
                root.interval = temp.interval
                root.right = self._remove(root.right, temp.meeting)
            else:
                # If start time is same but different meeting, we have to check both sides if they allow equal starts.
                # In our insert, equal starts go to right.
                root.right = self._remove(root.right, meeting)

        self._update_max(root)
        return root

    def _min_value_node(self, node: IntervalTreeNode) -> IntervalTreeNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def _update_max(self, root: IntervalTreeNode) -> None:
        root.max_end = root.interval.end_time
        if root.left and root.left.max_end > root.max_end:
            root.max_end = root.left.max_end
        if root.right and root.right.max_end > root.max_end:
            root.max_end = root.right.max_end

    def has_overlap(self, interval: Interval) -> bool:
        return self._has_overlap(self.root, interval)

    def _has_overlap(self, root: Optional[IntervalTreeNode], interval: Interval) -> bool:
        if root is None:
            return False

        if root.interval.overlaps(interval):
            return True

        if root.left and root.left.max_end > interval.start_time:
            if self._has_overlap(root.left, interval):
                return True

        return self._has_overlap(root.right, interval)

    def get_all_meetings(self) -> List[Meeting]:
        meetings = []
        self._in_order(self.root, meetings)
        return meetings

    def _in_order(self, root: Optional[IntervalTreeNode], meetings: List[Meeting]) -> None:
        if root is not None:
            self._in_order(root.left, meetings)
            meetings.append(root.meeting)
            self._in_order(root.right, meetings)
