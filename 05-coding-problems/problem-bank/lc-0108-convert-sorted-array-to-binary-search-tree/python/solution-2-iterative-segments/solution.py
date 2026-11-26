from collections import deque

class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:
        if not nums:
            return None
        mid = (len(nums) - 1) // 2
        root = TreeNode(nums[mid])
        queue = deque([(root, 0, mid - 1, True), (root, mid + 1, len(nums) - 1, False)])
        while queue:
            parent, left, right, attach_left = queue.popleft()
            if left > right:
                continue
            child_mid = (left + right) // 2
            child = TreeNode(nums[child_mid])
            if attach_left:
                parent.left = child
            else:
                parent.right = child
            queue.append((child, left, child_mid - 1, True))
            queue.append((child, child_mid + 1, right, False))
        return root
