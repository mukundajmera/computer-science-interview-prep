class Solution {
    public boolean canJump(int[] nums) {
        boolean[] reachable = new boolean[nums.length];
        reachable[0] = true;
        for (int target = 1; target < nums.length; target++) {
            for (int start = 0; start < target; start++) {
                if (reachable[start] && start + nums[start] >= target) {
                    reachable[target] = true;
                    break;
                }
            }
        }
        return reachable[nums.length - 1];
    }
}
