class Solution {
    public int[] maxSlidingWindow(int[] nums, int k) {
        int[] answer = new int[nums.length - k + 1];
        for (int start = 0; start <= nums.length - k; start++) {
            int max = nums[start];
            for (int index = start + 1; index < start + k; index++) {
                max = Math.max(max, nums[index]);
            }
            answer[start] = max;
        }
        return answer;
    }
}
