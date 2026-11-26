import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

class Solution {
    public List<Integer> findClosestElements(int[] arr, int k, int x) {
        List<Integer> values = new ArrayList<>();
        for (int value : arr) {
            values.add(value);
        }
        values.sort((left, right) -> {
            long byDistance = Math.abs((long) left - x) - Math.abs((long) right - x);
            if (byDistance < 0) {
                return -1;
            }
            if (byDistance > 0) {
                return 1;
            }
            return Integer.compare(left, right);
        });
        List<Integer> answer = new ArrayList<>(values.subList(0, k));
        Collections.sort(answer);
        return answer;
    }
}
