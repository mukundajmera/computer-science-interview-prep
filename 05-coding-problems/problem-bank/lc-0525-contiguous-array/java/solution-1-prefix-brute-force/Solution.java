class Solution {
    public int findMaxLength(int[] nums) {
        int[] prefix = new int[nums.length + 1];
        for (int i = 0; i < nums.length; i++) {
            prefix[i + 1] = prefix[i] + (nums[i] == 1 ? 1 : -1);
        }
        int best = 0;
        for (int start = 0; start < prefix.length; start++) {
            for (int end = start + 1; end < prefix.length; end++) {
                if (prefix[start] == prefix[end]) {
                    best = Math.max(best, end - start);
                }
            }
        }
        return best;
    }
}
