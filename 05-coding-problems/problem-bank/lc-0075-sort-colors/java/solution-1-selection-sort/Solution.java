class Solution {
    public void sortColors(int[] nums) {
        for (int index = 0; index < nums.length; index++) {
            int smallest = index;
            for (int scan = index + 1; scan < nums.length; scan++) {
                if (nums[scan] < nums[smallest]) {
                    smallest = scan;
                }
            }
            int temp = nums[index];
            nums[index] = nums[smallest];
            nums[smallest] = temp;
        }
    }
}
