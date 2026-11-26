import java.util.ArrayList;
import java.util.List;

class Solution {
    public void moveZeroes(int[] nums) {
        List<Integer> nonZeroes = new ArrayList<>();
        for (int num : nums) {
            if (num != 0) {
                nonZeroes.add(num);
            }
        }
        int index = 0;
        while (index < nonZeroes.size()) {
            nums[index] = nonZeroes.get(index);
            index++;
        }
        while (index < nums.length) {
            nums[index] = 0;
            index++;
        }
    }
}
