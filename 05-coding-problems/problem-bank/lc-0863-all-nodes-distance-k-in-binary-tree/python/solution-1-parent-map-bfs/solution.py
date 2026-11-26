from collections import deque
from typing import Dict, List, Optional


class Solution:
    def distanceK(self, root: Optional[TreeNode], target: Optional[TreeNode], k: int) -> List[int]:
        parent: Dict[TreeNode, Optional[TreeNode]] = {}

        def build(node: Optional[TreeNode], par: Optional[TreeNode]) -> None:
            if node is None:
                return
            parent[node] = par
            build(node.left, node)
            build(node.right, node)

        build(root, None)
        queue = deque([target])
        seen = {target}
        distance = 0
        while queue and distance < k:
            for _ in range(len(queue)):
                node = queue.popleft()
                for nxt in (node.left, node.right, parent.get(node)):
                    if nxt is not None and nxt not in seen:
                        seen.add(nxt)
                        queue.append(nxt)
            distance += 1
        return [node.val for node in queue]
