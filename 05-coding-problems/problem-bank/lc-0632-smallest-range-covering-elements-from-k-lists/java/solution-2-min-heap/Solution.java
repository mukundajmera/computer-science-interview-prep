import java.util.List;
import java.util.PriorityQueue;

class Solution {
    public int[] smallestRange(List<List<Integer>> nums) {
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> Integer.compare(a[0], b[0]));
        int currentMax = Integer.MIN_VALUE;
        for (int list = 0; list < nums.size(); list++) {
            int value = nums.get(list).get(0);
            heap.add(new int[] {value, list, 0});
            currentMax = Math.max(currentMax, value);
        }
        int[] best = {heap.peek()[0], currentMax};
        while (heap.size() == nums.size()) {
            int[] item = heap.remove();
            int currentMin = item[0];
            if (currentMax - currentMin < best[1] - best[0] || (currentMax - currentMin == best[1] - best[0] && currentMin < best[0])) {
                best = new int[] {currentMin, currentMax};
            }
            int nextIndex = item[2] + 1;
            if (nextIndex == nums.get(item[1]).size()) {
                break;
            }
            int nextValue = nums.get(item[1]).get(nextIndex);
            currentMax = Math.max(currentMax, nextValue);
            heap.add(new int[] {nextValue, item[1], nextIndex});
        }
        return best;
    }
}
