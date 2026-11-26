class Solution {
    public int firstBadVersion(int n, int firstBad) {
        for (int version = 1; version <= n; version++) {
            if (isBadVersion(version, firstBad)) {
                return version;
            }
        }
        return n;
    }

    private boolean isBadVersion(int version, int firstBad) {
        return version >= firstBad;
    }
}
