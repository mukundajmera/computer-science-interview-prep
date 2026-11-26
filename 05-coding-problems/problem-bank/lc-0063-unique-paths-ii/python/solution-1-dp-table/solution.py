class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
        rows = len(obstacleGrid)
        cols = len(obstacleGrid[0])
        if obstacleGrid[0][0] == 1:
            return 0
        dp = [[0] * cols for _ in range(rows)]
        dp[0][0] = 1
        for row in range(rows):
            for col in range(cols):
                if obstacleGrid[row][col] == 1:
                    dp[row][col] = 0
                else:
                    if row > 0:
                        dp[row][col] += dp[row - 1][col]
                    if col > 0:
                        dp[row][col] += dp[row][col - 1]
        return dp[-1][-1]
