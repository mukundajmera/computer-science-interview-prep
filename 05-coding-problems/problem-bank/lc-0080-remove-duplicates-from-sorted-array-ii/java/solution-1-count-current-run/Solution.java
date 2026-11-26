class Solution {
    public int removeDuplicates(int[] nums) {
        if (nums.length <= 2) {
            return nums.length;
        }
        int write = 0;
        int current = 0;
        int count = 0;
        boolean hasCurrent = false;
        for (int num : nums) {
            if (!hasCurrent || num != current) {
                current = num;
                count = 1;
                hasCurrent = true;
            } else {
                count++;
            }
            if (count <= 2) {
                nums[write] = num;
                write++;
            }
        }
        return write;
    }
}
