import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public int[] intersection(int[] nums1, int[] nums2) {
        int[] left = Arrays.copyOf(nums1, nums1.length);
        int[] right = Arrays.copyOf(nums2, nums2.length);
        Arrays.sort(left);
        Arrays.sort(right);

        List<Integer> shared = new ArrayList<>();
        int i = 0;
        int j = 0;
        while (i < left.length && j < right.length) {
            int leftValue = left[i];
            int rightValue = right[j];
            if (leftValue == rightValue) {
                shared.add(leftValue);
                while (i < left.length && left[i] == leftValue) {
                    i++;
                }
                while (j < right.length && right[j] == rightValue) {
                    j++;
                }
            } else if (leftValue < rightValue) {
                while (i < left.length && left[i] == leftValue) {
                    i++;
                }
            } else {
                while (j < right.length && right[j] == rightValue) {
                    j++;
                }
            }
        }

        int[] result = new int[shared.size()];
        for (int index = 0; index < shared.size(); index++) {
            result[index] = shared.get(index);
        }
        return result;
    }
}
