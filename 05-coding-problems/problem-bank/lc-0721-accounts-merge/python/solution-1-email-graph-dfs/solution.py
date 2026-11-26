from collections import defaultdict
from typing import List


class Solution:
    def accountsMerge(self, accounts: List[List[str]]) -> List[List[str]]:
        graph = defaultdict(list)
        name_by_email = {}
        for account in accounts:
            name = account[0]
            for index in range(1, len(account)):
                email = account[index]
                name_by_email[email] = name
                graph[email]
                if index > 1:
                    prev = account[index - 1]
                    graph[email].append(prev)
                    graph[prev].append(email)

        result = []
        seen = set()
        for email in graph:
            if email in seen:
                continue
            seen.add(email)
            stack = [email]
            component = []
            while stack:
                current = stack.pop()
                component.append(current)
                for nxt in graph[current]:
                    if nxt not in seen:
                        seen.add(nxt)
                        stack.append(nxt)
            result.append([name_by_email[email]] + sorted(component))
        return result
