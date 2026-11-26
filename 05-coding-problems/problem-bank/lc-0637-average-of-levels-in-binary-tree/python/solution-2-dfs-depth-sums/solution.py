from __future__ import annotations


class Solution:
    def averageOfLevels(self, root: Optional[TreeNode]) -> list[float]:
        sums: list[float] = []
        counts: list[int] = []

        def collect(node: Optional[TreeNode], depth: int) -> None:
            if node is None:
                return
            if depth == len(sums):
                sums.append(0.0)
                counts.append(0)
            sums[depth] += node.val
            counts[depth] += 1
            collect(node.left, depth + 1)
            collect(node.right, depth + 1)

        collect(root, 0)
        return [sums[index] / counts[index] for index in range(len(sums))]
