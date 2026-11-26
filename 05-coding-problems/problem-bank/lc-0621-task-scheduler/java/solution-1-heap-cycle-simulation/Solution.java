import java.util.PriorityQueue;

class Solution {
    public int leastInterval(char[] tasks, int n) {
        int[] counts = new int[26];
        for (char task : tasks) {
            counts[task - 'A']++;
        }
        PriorityQueue<Integer> heap = new PriorityQueue<>((a, b) -> b - a);
        for (int count : counts) {
            if (count > 0) {
                heap.add(count);
            }
        }
        int time = 0;
        while (!heap.isEmpty()) {
            int slots = n + 1;
            PriorityQueue<Integer> used = new PriorityQueue<>((a, b) -> b - a);
            while (slots > 0 && !heap.isEmpty()) {
                int remaining = heap.remove() - 1;
                if (remaining > 0) {
                    used.add(remaining);
                }
                time++;
                slots--;
            }
            heap.addAll(used);
            if (!heap.isEmpty()) {
                time += slots;
            }
        }
        return time;
    }
}
