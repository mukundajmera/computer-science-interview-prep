class Solution {
    public int largestRectangleArea(int[] heights) {
        int best = 0;
        for (int left = 0; left < heights.length; left++) {
            int minHeight = Integer.MAX_VALUE;
            for (int right = left; right < heights.length; right++) {
                minHeight = Math.min(minHeight, heights[right]);
                best = Math.max(best, minHeight * (right - left + 1));
            }
        }
        return best;
    }
}
