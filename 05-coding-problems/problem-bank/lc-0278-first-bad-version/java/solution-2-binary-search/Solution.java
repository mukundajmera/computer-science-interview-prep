class Solution {
    public int firstBadVersion(int n, int firstBad) {
        int left = 1;
        int right = n;
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (isBadVersion(mid, firstBad)) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left;
    }

    private boolean isBadVersion(int version, int firstBad) {
        return version >= firstBad;
    }
}
