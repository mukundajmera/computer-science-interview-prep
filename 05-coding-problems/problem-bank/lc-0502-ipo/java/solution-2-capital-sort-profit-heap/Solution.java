import java.util.Arrays;
import java.util.PriorityQueue;

class Solution {
    public int findMaximizedCapital(int k, int w, int[] profits, int[] capital) {
        int[][] projects = new int[profits.length][2];
        for (int i = 0; i < profits.length; i++) {
            projects[i][0] = capital[i];
            projects[i][1] = profits[i];
        }
        Arrays.sort(projects, (a, b) -> Integer.compare(a[0], b[0]));
        PriorityQueue<Integer> heap = new PriorityQueue<>((a, b) -> Integer.compare(b, a));
        int current = w;
        int index = 0;
        for (int round = 0; round < k; round++) {
            while (index < projects.length && projects[index][0] <= current) {
                heap.offer(projects[index][1]);
                index++;
            }
            if (heap.isEmpty()) {
                break;
            }
            current += heap.poll();
        }
        return current;
    }
}
