
import collections
import heapq

class Solutions:
    def canFinish(self, numCourses, prerequisites):
        indegree = [0] * numCourses
        adj = collections.defaultdict(list)
        for dest, src in prerequisites:
            adj[src].append(dest)
            indegree[dest] += 1
            
        q = collections.deque([i for i in range(numCourses) if indegree[i] == 0])
        count = 0
        while q:
            curr = q.popleft()
            count += 1
            for nxt in adj[curr]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)
        return count == numCourses

    def findOrder(self, numCourses, prerequisites):
        indegree = [0] * numCourses
        adj = collections.defaultdict(list)
        for dest, src in prerequisites:
            adj[src].append(dest)
            indegree[dest] += 1
            
        q = collections.deque([i for i in range(numCourses) if indegree[i] == 0])
        order = []
        while q:
            curr = q.popleft()
            order.append(curr)
            for nxt in adj[curr]:
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    q.append(nxt)
        return order if len(order) == numCourses else []

    def validTree(self, n, edges):
        if len(edges) != n - 1:
            return False
        adj = collections.defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        visited = set()
        def dfs(node, parent):
            if node in visited:
                return False
            visited.add(node)
            for neighbor in adj[node]:
                if neighbor != parent:
                    if not dfs(neighbor, node):
                        return False
            return True
            
        if not dfs(0, -1):
            return False
        return len(visited) == n

    def alienOrder(self, words):
        adj = {c: set() for w in words for c in w}
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i+1]
            min_len = min(len(w1), len(w2))
            if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
                return ""
            for j in range(min_len):
                if w1[j] != w2[j]:
                    adj[w1[j]].add(w2[j])
                    break
                    
        visited = {}
        res = []
        def dfs(c):
            if c in visited:
                return visited[c]
            visited[c] = True
            for nxt in adj[c]:
                if dfs(nxt):
                    return True
            visited[c] = False
            res.append(c)
            return False
            
        for c in adj:
            if dfs(c):
                return ""
        res.reverse()
        return "".join(res)

    def networkDelayTime(self, times, n, k):
        adj = collections.defaultdict(list)
        for u, v, w in times:
            adj[u].append((v, w))
            
        min_heap = [(0, k)]
        visited = set()
        t = 0
        while min_heap:
            w1, n1 = heapq.heappop(min_heap)
            if n1 in visited:
                continue
            visited.add(n1)
            t = max(t, w1)
            for n2, w2 in adj[n1]:
                if n2 not in visited:
                    heapq.heappush(min_heap, (w1 + w2, n2))
        return t if len(visited) == n else -1

    def findCheapestPrice(self, n, flights, src, dst, k):
        prices = [float("inf")] * n
        prices[src] = 0
        
        for i in range(k + 1):
            tmp_prices = list(prices)
            for s, d, p in flights:
                if prices[s] == float("inf"):
                    continue
                if prices[s] + p < tmp_prices[d]:
                    tmp_prices[d] = prices[s] + p
            prices = tmp_prices
            
        return prices[dst] if prices[dst] != float("inf") else -1

    def minCostConnectPoints(self, points):
        N = len(points)
        adj = {i: [] for i in range(N)}
        for i in range(N):
            x1, y1 = points[i]
            for j in range(i + 1, N):
                x2, y2 = points[j]
                dist = abs(x1 - x2) + abs(y1 - y2)
                adj[i].append((dist, j))
                adj[j].append((dist, i))
                
        res = 0
        visit = set()
        min_heap = [(0, 0)]
        while len(visit) < N:
            cost, i = heapq.heappop(min_heap)
            if i in visit:
                continue
            res += cost
            visit.add(i)
            for nei_cost, nei in adj[i]:
                if nei not in visit:
                    heapq.heappush(min_heap, (nei_cost, nei))
        return res
