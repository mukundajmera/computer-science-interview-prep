from typing import List
import collections

class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [1] * n
        self.count = n

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            self.count -= 1
            return True
        return False

class Solution:
    def findCircleNum(self, isConnected: List[List[int]]) -> int:
        if not isConnected:
            return 0
        n = len(isConnected)
        uf = UnionFind(n)
        for i in range(n):
            for j in range(i + 1, n):
                if isConnected[i][j] == 1:
                    uf.union(i, j)
        return uf.count

    def findRedundantConnection(self, edges: List[List[int]]) -> List[int]:
        uf = UnionFind(len(edges) + 1)
        for u, v in edges:
            if not uf.union(u, v):
                return [u, v]
        return []

    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        uf = UnionFind(n)
        for u, v in edges:
            uf.union(u, v)
        return uf.count

    def validTree(self, n: int, edges: List[List[int]]) -> bool:
        if len(edges) != n - 1:
            return False
        uf = UnionFind(n)
        for u, v in edges:
            if not uf.union(u, v):
                return False
        return True

    def accountsMerge(self, accounts: List[List[str]]) -> List[List[str]]:
        email_to_id = {}
        email_to_name = {}
        id_counter = 0
        for account in accounts:
            name = account[0]
            for email in account[1:]:
                if email not in email_to_id:
                    email_to_id[email] = id_counter
                    id_counter += 1
                email_to_name[email] = name
        
        uf = UnionFind(id_counter)
        for account in accounts:
            first_email_id = email_to_id[account[1]]
            for email in account[2:]:
                uf.union(first_email_id, email_to_id[email])
                
        id_to_emails = collections.defaultdict(list)
        for email, email_id in email_to_id.items():
            root_id = uf.find(email_id)
            id_to_emails[root_id].append(email)
            
        res = []
        for emails in id_to_emails.values():
            name = email_to_name[emails[0]]
            res.append([name] + sorted(emails))
        return res

    def longestConsecutive(self, nums: List[int]) -> int:
        if not nums: return 0
        nums = list(set(nums))
        n = len(nums)
        uf = UnionFind(n)
        
        val_to_idx = {val: i for i, val in enumerate(nums)}
        for val, i in val_to_idx.items():
            if val - 1 in val_to_idx:
                uf.union(i, val_to_idx[val - 1])
            if val + 1 in val_to_idx:
                uf.union(i, val_to_idx[val + 1])
                
        counts = collections.defaultdict(int)
        for i in range(n):
            counts[uf.find(i)] += 1
        return max(counts.values())
