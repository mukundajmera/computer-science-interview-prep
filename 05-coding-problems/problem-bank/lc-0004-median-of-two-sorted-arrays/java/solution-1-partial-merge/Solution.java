class Solution {
    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        int total = nums1.length + nums2.length;
        int middle = total / 2;
        int left = 0;
        int right = 0;
        int previous = 0;
        int current = 0;

        for (int step = 0; step <= middle; step++) {
            previous = current;
            if (right >= nums2.length || (left < nums1.length && nums1[left] <= nums2[right])) {
                current = nums1[left++];
            } else {
                current = nums2[right++];
            }
        }

        if ((total & 1) == 1) {
            return current;
        }
        return ((double) previous + (double) current) / 2.0;
    }
}
