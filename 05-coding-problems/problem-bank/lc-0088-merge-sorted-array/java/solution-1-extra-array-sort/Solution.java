import java.util.Arrays;

class Solution {
    public void merge(int[] nums1, int m, int[] nums2, int n) {
        int[] merged = new int[m + n];
        for (int index = 0; index < m; index++) {
            merged[index] = nums1[index];
        }
        for (int index = 0; index < n; index++) {
            merged[m + index] = nums2[index];
        }
        Arrays.sort(merged);
        for (int index = 0; index < merged.length; index++) {
            nums1[index] = merged[index];
        }
    }
}
