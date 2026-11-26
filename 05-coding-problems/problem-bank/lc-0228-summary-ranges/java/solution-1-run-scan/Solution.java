import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<String> summaryRanges(int[] nums) {
        List<String> result = new ArrayList<>();
        int index = 0;
        while (index < nums.length) {
            int start = nums[index];
            while (index + 1 < nums.length && nums[index + 1] == nums[index] + 1) {
                index++;
            }
            int end = nums[index];
            result.add(start == end ? String.valueOf(start) : start + "->" + end);
            index++;
        }
        return result;
    }
}
