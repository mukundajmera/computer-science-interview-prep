import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.Map;
import java.util.Queue;

class Solution {
    public int[] anagramMappings(int[] nums1, int[] nums2) {
        Map<Integer, Queue<Integer>> positions = new HashMap<>();
        for (int i = 0; i < nums2.length; i++) {
            positions.computeIfAbsent(nums2[i], ignored -> new ArrayDeque<>()).add(i);
        }
        int[] result = new int[nums1.length];
        for (int i = 0; i < nums1.length; i++) {
            result[i] = positions.get(nums1[i]).remove();
        }
        return result;
    }
}
