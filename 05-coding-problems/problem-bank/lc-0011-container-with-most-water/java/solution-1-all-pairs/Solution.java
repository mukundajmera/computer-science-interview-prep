class Solution {
    public int maxArea(int[] height) {
        int best = 0;
        for (int left = 0; left < height.length; left++) {
            for (int right = left + 1; right < height.length; right++) {
                int area = (right - left) * Math.min(height[left], height[right]);
                best = Math.max(best, area);
            }
        }
        return best;
    }
}
