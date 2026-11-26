from collections import deque

class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        if amount == 0:
            return 0
        visited = [False] * (amount + 1)
        queue = deque([0])
        visited[0] = True
        steps = 0
        while queue:
            steps += 1
            for _ in range(len(queue)):
                current = queue.popleft()
                for coin in coins:
                    next_amount = current + coin
                    if next_amount == amount:
                        return steps
                    if next_amount < amount and not visited[next_amount]:
                        visited[next_amount] = True
                        queue.append(next_amount)
        return -1
