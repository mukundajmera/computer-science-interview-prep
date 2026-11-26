class Solution {
    public int countComponents(int n, int[][] edges) {
        UnionFind unionFind = new UnionFind(n);
        int components = n;
        for (int[] edge : edges) {
            if (unionFind.union(edge[0], edge[1])) {
                components--;
            }
        }
        return components;
    }

    private static class UnionFind {
        private final int[] parent;
        private final int[] rank;

        UnionFind(int size) {
            parent = new int[size];
            rank = new int[size];
            for (int i = 0; i < size; i++) {
                parent[i] = i;
            }
        }

        int find(int value) {
            if (parent[value] != value) {
                parent[value] = find(parent[value]);
            }
            return parent[value];
        }

        boolean union(int left, int right) {
            int rootLeft = find(left);
            int rootRight = find(right);
            if (rootLeft == rootRight) {
                return false;
            }
            if (rank[rootLeft] < rank[rootRight]) {
                parent[rootLeft] = rootRight;
            } else if (rank[rootLeft] > rank[rootRight]) {
                parent[rootRight] = rootLeft;
            } else {
                parent[rootRight] = rootLeft;
                rank[rootLeft]++;
            }
            return true;
        }
    }
}
