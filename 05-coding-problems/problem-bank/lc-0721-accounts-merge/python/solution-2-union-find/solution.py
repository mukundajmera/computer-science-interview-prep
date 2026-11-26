from collections import defaultdict
from typing import Dict, List


class Solution:
    def accountsMerge(self, accounts: List[List[str]]) -> List[List[str]]:
        parent: Dict[str, str] = {}

        def find(email: str) -> str:
            parent.setdefault(email, email)
            if parent[email] != email:
                parent[email] = find(parent[email])
            return parent[email]

        def union(left: str, right: str) -> None:
            parent[find(left)] = find(right)

        name_by_email = {}
        for account in accounts:
            first = account[1]
            for email in account[1:]:
                name_by_email[email] = account[0]
                union(first, email)

        groups = defaultdict(list)
        for email in name_by_email:
            groups[find(email)].append(email)
        return [[name_by_email[emails[0]]] + sorted(emails) for emails in groups.values()]
