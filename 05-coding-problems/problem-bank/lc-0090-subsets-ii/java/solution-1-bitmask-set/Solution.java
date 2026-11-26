import java.util.*;
class Solution {
    public List<List<Integer>> subsetsWithDup(int[] nums) {
        Arrays.sort(nums);
        Set<List<Integer>> rows = new HashSet<>();
        int total = 1 << nums.length;
        for (int mask = 0; mask < total; mask++) {
            List<Integer> row = new ArrayList<>();
            for (int i = 0; i < nums.length; i++) if ((mask & (1 << i)) != 0) row.add(nums[i]);
            rows.add(row);
        }
        return new ArrayList<>(rows);
    }
}
