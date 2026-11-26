import sys
from typing import List


class Solution:
    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        sys.setrecursionlimit(max(sys.getrecursionlimit(), numCourses + 10))
        graph = [[] for _ in range(numCourses)]
        for course, prereq in prerequisites:
            graph[prereq].append(course)
        state = [0] * numCourses

        def dfs(course: int) -> bool:
            if state[course] == 1:
                return False
            if state[course] == 2:
                return True
            state[course] = 1
            for nxt in graph[course]:
                if not dfs(nxt):
                    return False
            state[course] = 2
            return True

        return all(dfs(course) for course in range(numCourses))
