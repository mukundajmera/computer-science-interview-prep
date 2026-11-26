import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

class Solution {
    public List<List<Integer>> kSmallestPairs(int[] nums1, int[] nums2, int k) {
        List<List<Integer>> result = new ArrayList<>();
        if (nums1.length == 0 || nums2.length == 0 || k <= 0) {
            return result;
        }
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> {
            int sumCompare = Integer.compare(a[0], b[0]);
            if (sumCompare != 0) {
                return sumCompare;
            }
            int firstCompare = Integer.compare(a[1], b[1]);
            if (firstCompare != 0) {
                return firstCompare;
            }
            return Integer.compare(a[2], b[2]);
        });
        for (int i = 0; i < Math.min(nums1.length, k); i++) {
            heap.offer(new int[] {nums1[i] + nums2[0], i, 0});
        }
        while (!heap.isEmpty() && result.size() < k) {
            int[] item = heap.poll();
            int i = item[1];
            int j = item[2];
            result.add(Arrays.asList(nums1[i], nums2[j]));
            if (j + 1 < nums2.length) {
                heap.offer(new int[] {nums1[i] + nums2[j + 1], i, j + 1});
            }
        }
        return result;
    }
}
