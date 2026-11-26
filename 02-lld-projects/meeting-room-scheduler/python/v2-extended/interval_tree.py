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
        
        # update max_end using children as well
        if root.left and root.left.max_end > root.max_end:
            root.max_end = root.left.max_end
        if root.right and root.right.max_end > root.max_end:
            root.max_end = root.right.max_end

        return root

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
