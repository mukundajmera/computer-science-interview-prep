import java.util.ArrayList;
import java.util.List;

class Solution {
    public int removeDuplicates(int[] nums) {
        if (nums.length == 0) {
            return 0;
        }
        List<Integer> unique = new ArrayList<>();
        unique.add(nums[0]);
        for (int index = 1; index < nums.length; index++) {
            if (nums[index] != nums[index - 1]) {
                unique.add(nums[index]);
            }
        }
        for (int index = 0; index < unique.size(); index++) {
            nums[index] = unique.get(index);
        }
        return unique.size();
    }
}
