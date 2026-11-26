import java.util.*;

class UnionFind {
    int[] parent;
    int[] rank;
    int count;

    public UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        count = n;
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            rank[i] = 1;
        }
    }

    public int find(int i) {
        if (parent[i] == i) {
            return i;
        }
        parent[i] = find(parent[i]);
        return parent[i];
    }

    public boolean union(int i, int j) {
        int rootI = find(i);
        int rootJ = find(j);
        if (rootI != rootJ) {
            if (rank[rootI] < rank[rootJ]) {
                parent[rootI] = rootJ;
            } else if (rank[rootI] > rank[rootJ]) {
                parent[rootJ] = rootI;
            } else {
                parent[rootJ] = rootI;
                rank[rootI]++;
            }
            count--;
            return true;
        }
        return false;
    }
}

public class Solutions {
    public int findCircleNum(int[][] isConnected) {
        if (isConnected == null || isConnected.length == 0) return 0;
        int n = isConnected.length;
        UnionFind uf = new UnionFind(n);
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                if (isConnected[i][j] == 1) {
                    uf.union(i, j);
                }
            }
        }
        return uf.count;
    }

    public int[] findRedundantConnection(int[][] edges) {
        UnionFind uf = new UnionFind(edges.length + 1);
        for (int[] edge : edges) {
            if (!uf.union(edge[0], edge[1])) {
                return edge;
            }
        }
        return new int[0];
    }

    public int countComponents(int n, int[][] edges) {
        UnionFind uf = new UnionFind(n);
        for (int[] edge : edges) {
            uf.union(edge[0], edge[1]);
        }
        return uf.count;
    }

    public boolean validTree(int n, int[][] edges) {
        if (edges.length != n - 1) return false;
        UnionFind uf = new UnionFind(n);
        for (int[] edge : edges) {
            if (!uf.union(edge[0], edge[1])) {
                return false;
            }
        }
        return true;
    }

    public List<List<String>> accountsMerge(List<List<String>> accounts) {
        Map<String, Integer> emailToId = new HashMap<>();
        Map<String, String> emailToName = new HashMap<>();
        int idCounter = 0;
        
        for (List<String> account : accounts) {
            String name = account.get(0);
            for (int i = 1; i < account.size(); i++) {
                String email = account.get(i);
                if (!emailToId.containsKey(email)) {
                    emailToId.put(email, idCounter++);
                }
                emailToName.put(email, name);
            }
        }
        
        UnionFind uf = new UnionFind(idCounter);
        for (List<String> account : accounts) {
            int firstEmailId = emailToId.get(account.get(1));
            for (int i = 2; i < account.size(); i++) {
                uf.union(firstEmailId, emailToId.get(account.get(i)));
            }
        }
        
        Map<Integer, List<String>> idToEmails = new HashMap<>();
        for (String email : emailToId.keySet()) {
            int rootId = uf.find(emailToId.get(email));
            idToEmails.computeIfAbsent(rootId, k -> new ArrayList<>()).add(email);
        }
        
        List<List<String>> res = new ArrayList<>();
        for (List<String> emails : idToEmails.values()) {
            Collections.sort(emails);
            String name = emailToName.get(emails.get(0));
            List<String> mergedAccount = new ArrayList<>();
            mergedAccount.add(name);
            mergedAccount.addAll(emails);
            res.add(mergedAccount);
        }
        return res;
    }

    public int longestConsecutive(int[] nums) {
        if (nums == null || nums.length == 0) return 0;
        Set<Integer> numSet = new HashSet<>();
        for (int num : nums) {
            numSet.add(num);
        }
        
        List<Integer> uniqueNums = new ArrayList<>(numSet);
        int n = uniqueNums.size();
        UnionFind uf = new UnionFind(n);
        
        Map<Integer, Integer> valToIdx = new HashMap<>();
        for (int i = 0; i < n; i++) {
            valToIdx.put(uniqueNums.get(i), i);
        }
        
        for (int i = 0; i < n; i++) {
            int val = uniqueNums.get(i);
            if (valToIdx.containsKey(val - 1)) {
                uf.union(i, valToIdx.get(val - 1));
            }
            if (valToIdx.containsKey(val + 1)) {
                uf.union(i, valToIdx.get(val + 1));
            }
        }
        
        Map<Integer, Integer> counts = new HashMap<>();
        int maxCount = 0;
        for (int i = 0; i < n; i++) {
            int root = uf.find(i);
            counts.put(root, counts.getOrDefault(root, 0) + 1);
            maxCount = Math.max(maxCount, counts.get(root));
        }
        return maxCount;
    }
}
