import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<Integer> findClosestElements(int[] arr, int k, int x) {
        int left = 0;
        int right = arr.length - 1;
        while (right - left + 1 > k) {
            long leftDistance = Math.abs((long) arr[left] - x);
            long rightDistance = Math.abs((long) arr[right] - x);
            if (leftDistance <= rightDistance) {
                right--;
            } else {
                left++;
            }
        }
        List<Integer> answer = new ArrayList<>();
        for (int index = left; index <= right; index++) {
            answer.add(arr[index]);
        }
        return answer;
    }
}
