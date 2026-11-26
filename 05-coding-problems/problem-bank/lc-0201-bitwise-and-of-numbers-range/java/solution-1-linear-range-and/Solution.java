class Solution {
    public int rangeBitwiseAnd(int left, int right) {
        long result = left;
        for (long value = (long) left + 1; value <= right; value++) {
            result &= value;
            if (result == 0) {
                return 0;
            }
        }
        return (int) result;
    }
}
