import java.util.ArrayList;
import java.util.List;

class Solution {
    public int removeElement(int[] nums, int val) {
        List<Integer> kept = new ArrayList<>();
        for (int num : nums) {
            if (num != val) {
                kept.add(num);
            }
        }
        for (int index = 0; index < kept.size(); index++) {
            nums[index] = kept.get(index);
        }
        return kept.size();
    }
}
