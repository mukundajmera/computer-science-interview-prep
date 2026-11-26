import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        Set<List<Integer>> unique = new LinkedHashSet<>();
        for (int i = 0; i < nums.length; i++) {
            for (int j = i + 1; j < nums.length; j++) {
                for (int k = j + 1; k < nums.length; k++) {
                    if (nums[i] + nums[j] + nums[k] == 0) {
                        Integer[] triplet = {nums[i], nums[j], nums[k]};
                        Arrays.sort(triplet);
                        unique.add(Arrays.asList(triplet));
                    }
                }
            }
        }
        List<List<Integer>> answer = new ArrayList<>(unique);
        answer.sort((a, b) -> {
            for (int i = 0; i < a.size(); i++) {
                int cmp = Integer.compare(a.get(i), b.get(i));
                if (cmp != 0) {
                    return cmp;
                }
            }
            return 0;
        });
        return answer;
    }
}
