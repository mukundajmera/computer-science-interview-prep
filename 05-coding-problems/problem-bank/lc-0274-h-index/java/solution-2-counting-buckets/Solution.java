class Solution {
    public int hIndex(int[] citations) {
        int n = citations.length;
        int[] buckets = new int[n + 1];
        for (int citation : citations) {
            buckets[Math.min(citation, n)]++;
        }
        int papers = 0;
        for (int h = n; h >= 0; h--) {
            papers += buckets[h];
            if (papers >= h) {
                return h;
            }
        }
        return 0;
    }
}
