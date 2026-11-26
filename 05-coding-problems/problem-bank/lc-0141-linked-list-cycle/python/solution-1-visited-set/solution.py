from __future__ import annotations

from typing import Optional


class Solution:
    def hasCycle(self, head: Optional[ListNode]) -> bool:
        seen: set[int] = set()
        current = head
        while current is not None:
            marker = id(current)
            if marker in seen:
                return True
            seen.add(marker)
            current = current.next
        return False
