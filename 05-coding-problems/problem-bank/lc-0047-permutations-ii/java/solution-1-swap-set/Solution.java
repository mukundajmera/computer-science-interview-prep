import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public List<List<Integer>> permuteUnique(int[] nums) {
        Set<List<Integer>> rows = new HashSet<>();
        permute(nums, 0, rows);
        return new ArrayList<>(rows);
    }

    private void permute(int[] nums, int index, Set<List<Integer>> rows) {
        if (index == nums.length) {
            List<Integer> row = new ArrayList<>();
            for (int value : nums) row.add(value);
            rows.add(row);
            return;
        }
        for (int i = index; i < nums.length; i++) {
            swap(nums, index, i);
            permute(nums, index + 1, rows);
            swap(nums, index, i);
        }
    }

    private void swap(int[] nums, int a, int b) {
        int temp = nums[a];
        nums[a] = nums[b];
        nums[b] = temp;
    }
}
