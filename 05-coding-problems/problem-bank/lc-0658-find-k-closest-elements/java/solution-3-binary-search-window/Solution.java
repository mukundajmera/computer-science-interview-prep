import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<Integer> findClosestElements(int[] arr, int k, int x) {
        int left = 0;
        int right = arr.length - k;
        while (left < right) {
            int mid = left + (right - left) / 2;
            long leftDistance = (long) x - arr[mid];
            long rightDistance = (long) arr[mid + k] - x;
            if (leftDistance > rightDistance) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }
        List<Integer> answer = new ArrayList<>();
        for (int index = left; index < left + k; index++) {
            answer.add(arr[index]);
        }
        return answer;
    }
}
