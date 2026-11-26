class Solution {
    public int mySqrt(int x) {
        long candidate = 0;
        while ((candidate + 1) * (candidate + 1) <= x) {
            candidate++;
        }
        return (int) candidate;
    }
}
