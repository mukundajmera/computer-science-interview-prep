class Solution {
    public void sortColors(int[] nums) {
        int[] counts = new int[3];
        for (int num : nums) {
            counts[num]++;
        }
        int index = 0;
        for (int color = 0; color < counts.length; color++) {
            for (int count = 0; count < counts[color]; count++) {
                nums[index] = color;
                index++;
            }
        }
    }
}
